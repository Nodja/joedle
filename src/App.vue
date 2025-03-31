<template>
  <div class="joedle-container">
    <h1>Joedle</h1>
    <p>Guess which Joseph Anderson video/stream the quote is from!</p>

    <div v-if="isLoading">Loading today's quote...</div>
    <div v-else-if="!solution">
      <p class="error-message">Could not find a quote for today ({{ todayKey }}). Please check quotes.json or try again tomorrow.</p>
    </div>
    <div v-else>
      <!-- Quote Display -->
      <blockquote class="quote-display">
        "{{ quoteDisplay }}"
      </blockquote>

      <!-- Guess Input & Autocomplete -->
      <div class="guess-area" v-if="!isGameOver">
        <div class="autocomplete-wrapper">
          <input
            type="text"
            v-model="currentGuessInput"
            @input="handleInput"
            @focus="showAutocomplete = true"
            @blur="hideAutocomplete"
            placeholder="Type your guess..."
            :disabled="isGameOver"
            aria-label="Guess the source"
            ref="guessInputRef"
          />
           <div class="autocomplete-placeholder" v-if="showAutocomplete && !currentGuessInput && !isGameOver">
            Start typing to show guesses...
           </div>
          <ul v-if="showAutocomplete && filteredOptions.length > 0 && currentGuessInput" class="autocomplete-list">
            <li
              v-for="option in filteredOptions"
              :key="option"
              @mousedown.prevent="selectOption(option)"
              tabindex="0"
              @keydown.enter="selectOption(option)"
            >
              {{ option }}
            </li>
          </ul>
        </div>
        <button @click="submitGuess" :disabled="!currentGuessInput || isGameOver || !isValidGuessFormat">Guess ({{ guessesRemaining }}/{{ MAX_GUESSES }})</button>
         <p v-if="currentGuessInput && !isValidGuessFormat && !showAutocomplete" class="input-warning">
            Select a valid option from the list.
         </p>
      </div>
      <p v-if="!isGameOver && guesses.length > 0" class="guesses-remaining-mobile">{{ guessesRemaining }} guesses remaining.</p>


      <!-- Guess History & Clues -->
      <div v-if="guesses.length > 0" class="guesses-history">
        <h2>Guesses:</h2>
        <table>
          <thead>
            <tr>
              <th>Guess</th>
              <th>Type</th>
              <th>Game</th>
              <th>Year</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(guess, index) in reversedGuesses" :key="index">
              <td>{{ guess.guessedTitle }}</td>
              <!-- Type Clue -->
              <td :class="getClueClass(guess.typeMatch)">
                <span v-if="guess.typeMatch">✅ {{ guess.guessedType }}</span>
                <span v-else>❌ {{ guess.guessedType }}</span>
              </td>
              <!-- Game Clue -->
               <td :class="getClueClass(guess.gameMatch)">
                 <span v-if="guess.gameMatch">✅ {{ guess.guessedGame }}</span>
                 <span v-else>❌ {{ guess.guessedGame }}</span>
              </td>
              <!-- Year Clue -->
              <td :class="getClueClass(guess.yearMatch === 'correct', guess.yearMatch !== 'correct' && guess.yearMatch !== 'unknown')">
                <span v-if="guess.yearMatch === 'correct'">✅ {{ guess.guessedYear }}</span>
                <span v-else-if="guess.yearMatch === 'higher'">⬇️ {{ guess.guessedYear }}</span> <!-- Correct year is lower -->
                <span v-else-if="guess.yearMatch === 'lower'">⬆️ {{ guess.guessedYear }}</span> <!-- Correct year is higher -->
                <span v-else>N/A</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Win State -->
      <div v-if="isWon" class="win-message state-message">
        <h2>Congratulations! You got it in {{ guesses.length }} {{ guesses.length === 1 ? 'guess' : 'guesses' }}!</h2>
        <p>
          The quote is from:
          <strong>{{ solution.type }} - {{ solution.title }}</strong>
          ({{ solution.year }})
        </p>
        <p>Game: <strong>{{ solution.game }}</strong></p>
        <p>
          <a :href="solution.url" target="_blank" rel="noopener noreferrer">
            Where did joe say that?
          </a>
        </p>
      </div>

      <!-- Loss State -->
      <div v-if="isLost" class="loss-message state-message">
        <h2>Out of guesses!</h2>
        <p>
          The correct answer was:
          <strong>{{ solution.type }} - {{ solution.title }}</strong>
          ({{ solution.year }})
        </p>
        <p>Game: <strong>{{ solution.game }}</strong></p>
        <p>
          <a :href="solution.url" target="_blank" rel="noopener noreferrer">
            Where did joe say that?
          </a>
        </p>
      </div>

      <!-- Stats and Share Section -->
      <div v-if="isGameOver" class="stats-share-section">
        <h2>Statistics</h2>
        <div class="stats-summary">
            <div>
                <div class="stat-value">{{ gameStats.played }}</div>
                <div class="stat-label">Played</div>
            </div>
            <div>
                <div class="stat-value">{{ winPercentage }}%</div>
                <div class="stat-label">Win %</div>
            </div>
             <div>
                <div class="stat-value">{{ gameStats.currentStreak }}</div>
                <div class="stat-label">Current Streak</div>
            </div>
             <div>
                <div class="stat-value">{{ gameStats.maxStreak }}</div>
                <div class="stat-label">Max Streak</div>
            </div>
        </div>

        <h3>Guess Distribution</h3>
        <div class="histogram">
            <div v-for="i in MAX_GUESSES" :key="i" class="histogram-row">
                <div class="histogram-label">{{ i }}</div>
                <div class="histogram-bar-container">
                    <div class="histogram-bar" :style="{ width: calculateBarWidth(gameStats.wins[i] || 0) }">
                        {{ gameStats.wins[i] || 0 }}
                    </div>
                </div>
            </div>
             <div class="histogram-row">
                <div class="histogram-label">X</div>
                <div class="histogram-bar-container">
                    <div class="histogram-bar loss-bar" :style="{ width: calculateBarWidth(gameStats.losses) }">
                        {{ gameStats.losses || 0 }}
                    </div>
                </div>
            </div>
        </div>

        <button @click="copyShareText" class="share-button">
          {{ shareStatus }}
        </button>
      </div>

      <hr v-if="!isLoading">

      <!-- Credits -->
       <div class="credits" v-if="!isLoading">
          <p>Quotes curated by: Number333 aka Quote-chan</p>
          <p>Background Fanart by Marik</p>
          <p>Site by: Nodja</p>
          <p><a href="https://github.com/nodja/joedle" target="_blank" rel="noopener noreferrer">Source Code</a></p>
       </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue';

// --- Constants ---
const MAX_GUESSES = 10; // Configurable guess limit
const STATS_STORAGE_KEY = 'joedle-stats';

// --- State ---
const quotesData = ref(null);
const isLoading = ref(true);
const todayKey = ref('');
const solution = ref(null);
const currentGuessInput = ref('');
const guesses = ref([]); // Stores { guessedTitle, guessedType, guessedGame, guessedYear, typeMatch, gameMatch, yearMatch }
const isWon = ref(false);
const showAutocomplete = ref(false);
const allPossibleOptions = ref([]); // Stores "Type - Title" strings
const guessInputRef = ref(null); // Ref for the input element
const shareStatus = ref('Share Results 📋'); // For share button feedback

// Game Stats State
const gameStats = ref({
    played: 0,
    wins: { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0 },
    losses: 0,
    currentStreak: 0,
    maxStreak: 0,
    lastPlayedKey: null, // To track if played today for streak
});

// --- Lifecycle ---
onMounted(async () => {
  todayKey.value = getTodayKey();
  // *** For Testing: Override todayKey if needed ***
  // todayKey.value = '2025-04-04'; // Example: Uncomment to test with a specific date

  loadStats(); // Load stats first
  await loadQuotes(); // Then load quotes

  if (quotesData.value) {
    solution.value = quotesData.value[todayKey.value] || null;
    if (solution.value) {
        generateAllOptions();
        loadDailyState(); // Load today's progress AFTER solution is known
    }
  }
  isLoading.value = false;
});

// --- Computed Properties ---
const quoteDisplay = computed(() => {
  if (solution.value?.quote && solution.value?.game) {
    return solution.value.quote.replace(/\[X\]/gi, solution.value.game);
  }
  return solution.value?.quote || '';
});

const filteredOptions = computed(() => {
  if (!currentGuessInput.value) {
    return [];
  }
  const searchTerm = currentGuessInput.value.toLowerCase();
  return allPossibleOptions.value.filter(option =>
    option.toLowerCase().includes(searchTerm)
  ).slice(0, 10);
});

const reversedGuesses = computed(() => {
  return guesses.value.slice().reverse();
});

const isValidGuessFormat = computed(() => {
    return allPossibleOptions.value.includes(currentGuessInput.value);
});

const guessesRemaining = computed(() => {
    return MAX_GUESSES - guesses.value.length;
});

const isLost = computed(() => {
    return guesses.value.length >= MAX_GUESSES && !isWon.value;
});

const isGameOver = computed(() => {
    return isWon.value || isLost.value;
});

const dailyStorageKey = computed(() => `joedle-state-${todayKey.value}`);

// Stats Computeds
const winPercentage = computed(() => {
    if (gameStats.value.played === 0) return 0;
    const totalWins = Object.values(gameStats.value.wins).reduce((sum, count) => sum + count, 0);
    return Math.round((totalWins / gameStats.value.played) * 100);
});

const maxWinCountForHistogram = computed(() => {
    const counts = [...Object.values(gameStats.value.wins), gameStats.value.losses];
    return Math.max(...counts, 1); // Return at least 1 to avoid division by zero if no games played
});


// --- Methods ---
function getTodayKey() {
  const today = new Date();
  // Use UTC date to avoid timezone issues changing the date across the world
  const year = today.getUTCFullYear();
  const month = String(today.getUTCMonth() + 1).padStart(2, '0');
  const day = String(today.getUTCDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

async function loadQuotes() {
  try {
    const response = await fetch('/quotes.json');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    quotesData.value = await response.json();
  } catch (error) {
    console.error("Failed to load quotes:", error);
    quotesData.value = null;
  }
}

function generateAllOptions() {
    if (!quotesData.value) return;
    // Filter options to only include unique "Type - Title" pairs present in the data
    const uniqueOptions = new Set();
    Object.values(quotesData.value).forEach(q => {
        if (q && q.type && q.title) { // Basic check for valid quote entry
           uniqueOptions.add(`${q.type} - ${q.title}`);
        }
    });
    allPossibleOptions.value = [...uniqueOptions].sort();
}

function handleInput() {
  showAutocomplete.value = true;
}

function hideAutocomplete() {
  setTimeout(() => {
    // Check if the focus is still within the component (e.g., on a list item)
    // This is tricky, using mousedown.prevent on items is often more reliable
    // const relatedTarget = event.relatedTarget;
    // if (!guessInputRef.value?.contains(relatedTarget)) {
       showAutocomplete.value = false;
    // }
  }, 200); // Delay allows click on dropdown items
}

function selectOption(option) {
  currentGuessInput.value = option;
  showAutocomplete.value = false;
  guessInputRef.value?.focus(); // Keep focus on input after selection
}

function findQuoteDataBySelection(selectionString) {
    if (!quotesData.value || !selectionString) return null;
    // Find *any* quote entry that matches the selected "Type - Title".
    // The exact date doesn't matter here, just the metadata.
    for (const key in quotesData.value) {
        const quote = quotesData.value[key];
         if (quote && quote.type && quote.title && `${quote.type} - ${quote.title}` === selectionString) {
            // Return a copy to avoid potential modification issues if needed later
             return { ...quote };
        }
    }
    console.warn("Could not find matching quote data for selection:", selectionString);
    return null;
}

function submitGuess() {
  if (!currentGuessInput.value || isGameOver.value || !solution.value || !isValidGuessFormat.value) {
    console.warn("Submit blocked:", {
        input: currentGuessInput.value, isGameOver: isGameOver.value, solutionExists: !!solution.value, isValid: isValidGuessFormat.value
    });
    return;
  }

  const guessedData = findQuoteDataBySelection(currentGuessInput.value);

  if (!guessedData) {
      console.error("Critical: Could not find data for validated guess:", currentGuessInput.value);
      // Show a user-facing error maybe?
      currentGuessInput.value = ''; // Clear invalid input state
      return;
  }

  // Ensure years are numbers for comparison
  const guessedYearNum = Number(guessedData.year);
  const solutionYearNum = Number(solution.value.year);

  const guessResult = {
    guessedTitle: currentGuessInput.value,
    guessedType: guessedData.type,
    guessedGame: guessedData.game,
    guessedYear: guessedYearNum, // Store as number
    typeMatch: guessedData.type === solution.value.type,
    gameMatch: guessedData.game === solution.value.game,
    yearMatch: compareYears(guessedYearNum, solutionYearNum)
  };

  guesses.value.push(guessResult);

  // Check for win condition (Exact match on title is the most direct way now)
  if (currentGuessInput.value === `${solution.value.type} - ${solution.value.title}`) {
     isWon.value = true;
   }
  // Alternatively, check components:
  // if (guessResult.typeMatch && guessResult.gameMatch && guessResult.yearMatch === 'correct') {
  //    isWon.value = true;
  // }

  currentGuessInput.value = ''; // Clear input after guess
  saveDailyState(); // Save progress after each guess
}

function compareYears(guessedYear, solutionYear) {
  if (isNaN(guessedYear) || isNaN(solutionYear)) return 'unknown'; // Handle cases where year might be missing/invalid
  if (guessedYear === solutionYear) return 'correct';
  if (guessedYear < solutionYear) return 'lower';
  if (guessedYear > solutionYear) return 'higher';
  return 'unknown'; // Fallback
}

function getClueClass(isCorrect, isNear = false) { // Added isNear for year
  if (isCorrect) return 'clue-correct';
  if (isNear) return 'clue-near'; // Style for up/down arrows if desired
  return 'clue-incorrect'; // Default incorrect style
}

// --- Local Storage Persistence ---

function saveDailyState() {
    if (!solution.value) return; // Don't save if there's no game for today
    try {
        const state = {
            guesses: guesses.value,
            isWon: isWon.value,
            // No need to save isLost, it's derivable
        };
        localStorage.setItem(dailyStorageKey.value, JSON.stringify(state));
    } catch (e) {
        console.error("Failed to save daily state to localStorage:", e);
    }
}

function loadDailyState() {
    if (!solution.value) return; // Don't load if there's no game for today
    try {
        const storedState = localStorage.getItem(dailyStorageKey.value);
        if (storedState) {
            const parsedState = JSON.parse(storedState);
            // Basic validation: Check if it looks like our state object
            if (parsedState && Array.isArray(parsedState.guesses) && typeof parsedState.isWon === 'boolean') {
                guesses.value = parsedState.guesses;
                isWon.value = parsedState.isWon;
                console.log("Loaded previous state for today:", parsedState);
            } else {
                console.warn("Invalid daily state found in localStorage. Resetting.");
                localStorage.removeItem(dailyStorageKey.value); // Clear invalid data
            }
        }
    } catch (e) {
        console.error("Failed to load or parse daily state from localStorage:", e);
        localStorage.removeItem(dailyStorageKey.value); // Clear potentially corrupted data
    }
}

// --- Statistics Handling ---

function loadStats() {
    try {
        const storedStats = localStorage.getItem(STATS_STORAGE_KEY);
        if (storedStats) {
            const parsed = JSON.parse(storedStats);
            // Merge loaded stats with default structure to ensure all keys exist
            gameStats.value = { ...gameStats.value, ...parsed };
            // Ensure wins object has all keys
             for (let i = 1; i <= MAX_GUESSES; i++) {
                 if (!(i in gameStats.value.wins)) {
                     gameStats.value.wins[i] = 0;
                 }
             }
             console.log("Loaded game stats:", gameStats.value);
        }
    } catch (e) {
        console.error("Failed to load or parse game stats from localStorage:", e);
        // Don't clear stats, just use defaults
    }
}

function saveStats() {
    try {
        localStorage.setItem(STATS_STORAGE_KEY, JSON.stringify(gameStats.value));
    } catch (e) {
        console.error("Failed to save game stats to localStorage:", e);
    }
}

function updateStats() {
    // Only update stats once per day when the game ends
    if (gameStats.value.lastPlayedKey === todayKey.value) {
      console.log("Stats already updated for today.");
      return; // Already updated today
    }

    const stats = gameStats.value; // Local mutable copy
    stats.played += 1;
    stats.lastPlayedKey = todayKey.value; // Mark as played today

    if (isWon.value) {
        const guessCount = guesses.value.length;
        if (guessCount >= 1 && guessCount <= MAX_GUESSES) {
            stats.wins[guessCount] = (stats.wins[guessCount] || 0) + 1;
        }
        stats.currentStreak += 1;
        stats.maxStreak = Math.max(stats.maxStreak, stats.currentStreak);
    } else if (isLost.value) {
        stats.losses = (stats.losses || 0) + 1;
        stats.currentStreak = 0; // Reset streak on loss
    }

    gameStats.value = stats; // Update the ref
    saveStats();
    console.log("Updated and saved stats:", gameStats.value);
}

// Watch for game over to update stats
watch(isGameOver, (newVal) => {
  if (newVal) {
    // Use nextTick to ensure DOM updates (like win/loss message) are potentially processed
    // although it might not be strictly necessary for stats calculation itself.
    // nextTick(() => {
        updateStats();
    // });
  }
});

// --- Histogram ---
function calculateBarWidth(count) {
    if (maxWinCountForHistogram.value === 0) return '0%'; // Avoid division by zero
    const percentage = (count / maxWinCountForHistogram.value) * 100;
    // Add a minimum width for visibility even for 0 counts if desired, e.g., return `max(5%, ${percentage}%)`
    return `${Math.max(percentage, 3)}%`; // Ensure even 0 count bars are slightly visible
}

// --- Share Functionality ---
function generateShareText() {
    if (!solution.value) return "Error generating share text.";

    const title = `Joedle ${todayKey.value}`;
    const score = isWon.value ? `${guesses.value.length}/${MAX_GUESSES}` : `X/${MAX_GUESSES}`;
    const header = `${score} ${title}\nhttps://joedle.nodja.com\n`;

    const grid = guesses.value.map(guess => {
        const typeEmoji = guess.typeMatch ? '🟩' : '🟥';
        const gameEmoji = guess.gameMatch ? '🟩' : '🟥';
        let yearEmoji = ' N/A '; // Default if unknown
        if (guess.yearMatch === 'correct') yearEmoji = '🟩';
        else if (guess.yearMatch === 'higher') yearEmoji = '⬇️'; // Guessed higher, arrow points down
        else if (guess.yearMatch === 'lower') yearEmoji = '⬆️'; // Guessed lower, arrow points up
        // Combine without spaces if preferred: return `${typeEmoji}${gameEmoji}${yearEmoji}`;
        return `${typeEmoji}${gameEmoji}${yearEmoji}`;
    }).join('\n');

    // Add link or hashtag if desired
    // const link = "\nhttps://your-joedle-url.com";
    // return header + grid + link;
    return header + '\n' + grid;
}

async function copyShareText() {
    const textToCopy = generateShareText();
    try {
        await navigator.clipboard.writeText(textToCopy);
        shareStatus.value = 'Copied! ✅';
        setTimeout(() => {
            shareStatus.value = 'Share Results 📋'; // Reset after a delay
        }, 2000);
    } catch (err) {
        console.error('Failed to copy share text: ', err);
        shareStatus.value = 'Copy Failed ❌';
         setTimeout(() => {
            shareStatus.value = 'Share Results 📋';
        }, 2000);
    }
}

</script>

<style scoped>
/* Reverted closer to original look + target image */
.joedle-container {
  font-family: sans-serif;
  max-width: 700px;
  margin: 20px auto;
  padding: 20px;
  border: 1px solid #333; /* Slightly darker border */
  border-radius: 8px;
  background-color: #21212150; /* Dark background */
  color: #e0e0e0; /* Light text */
}

h1, h2, h3 {
  text-align: center;
  color: #f5f5f5; /* Brighter title text */
}

h2 {
    margin-top: 30px;
    margin-bottom: 15px;
}
h3 {
    margin-top: 25px;
    margin-bottom: 10px;
}

hr {
    border: none;
    border-top: 1px solid #444; /* Lighter separator */
    margin: 30px 0;
}

.quote-display {
  background-color: #333; /* Darker quote background */
  border-left: 5px solid #007bff; /* Blue border */
  padding: 15px;
  margin: 20px 0;
  font-style: italic;
  font-size: 1.1em;
  color: #e0e0e0; /* Light text */
  border-radius: 4px;
}

.guess-area {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 5px;
  position: relative;
}

.autocomplete-wrapper {
   flex-grow: 1;
   position: relative;
}

.guess-area input[type="text"] {
  flex-grow: 1;
  padding: 10px;
  font-size: 1em;
  border: 1px solid #666; /* Visible border */
  border-radius: 4px;
  width: 100%;
  box-sizing: border-box;
  background-color: #444; /* Lighter input background */
  color: #e0e0e0; /* Light input text */
}

.guess-area input[type="text"]::placeholder {
  color: #999; /* Darker placeholder */
}

.guess-area button {
  padding: 10px 15px;
  font-size: 1em;
  cursor: pointer;
  background-color: #555; /* Grey button background */
  color: #e0e0e0; /* Light text */
  border: 1px solid #666;
  border-radius: 4px;
  transition: background-color 0.2s ease;
  white-space: nowrap;
  height: 42px; /* Match input height */
  box-sizing: border-box;
}

.guess-area button:disabled {
  background-color: #333; /* Darker disabled background */
  color: #777; /* Dimmer text */
  border-color: #444;
  cursor: not-allowed;
}

.guess-area button:not(:disabled):hover {
  background-color: #666; /* Slightly lighter grey on hover */
}

.input-warning {
    color: #ff8a80; /* Lighter red */
    font-size: 0.9em;
    margin-top: 5px;
    width: 100%;
    text-align: left;
    padding-left: 5px;
}

.guesses-remaining-mobile {
    display: none;
    text-align: center;
    margin: 10px 0;
    font-size: 0.9em;
    color: #aaa; /* Placeholder color */
}

.autocomplete-placeholder {
  position: absolute;
  top: 100%;
  left: 0;
  width: calc(100% - 2px);
  background-color: #444; /* Match input background */
  color: #999; /* Match placeholder */
  padding: 8px 12px;
  border: 1px solid #666;
  border-top: none;
  box-shadow: 0 4px 6px rgba(0,0,0,0.3); /* Darker shadow */
  border-radius: 0 0 4px 4px;
  z-index: 10;
  font-size: 0.9em;
  font-style: italic;
  box-sizing: border-box;
}


.autocomplete-list {
  list-style: none;
  margin: 0;
  padding: 0;
  border: 1px solid #666;
  border-top: none;
  max-height: 200px;
  overflow-y: auto;
  background-color: #444; /* Match input */
  color: #e0e0e0; /* Light text */
  position: absolute;
  width: 100%;
  z-index: 10;
  box-shadow: 0 4px 6px rgba(0,0,0,0.3);
  border-radius: 0 0 4px 4px;
  box-sizing: border-box;
}

.autocomplete-list li {
  padding: 8px 12px;
  cursor: pointer;
}

.autocomplete-list li:hover,
.autocomplete-list li:focus {
  background-color: #555; /* Slightly darker hover */
  outline: none;
}

.guesses-history {
  margin-top: 20px;
}

.guesses-history table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}

.guesses-history th,
.guesses-history td {
  border: 1px solid #555; /* Darker border */
  padding: 8px 12px;
  text-align: center;
  vertical-align: middle;
  background-color: #3a3a3a; /* Default dark cell background */
  color: #e0e0e0; /* Light text */
  transition: background-color 0.5s ease;
}

.guesses-history th {
  background-color: #4f4f4f; /* Slightly different header background */
  font-weight: bold;
  color: #f5f5f5;
}

/* Clue Styling */
.clue-correct {
  background-color: #2e7d32 !important; /* Vibrant Green */
  color: #fff !important;
}
.clue-near {
  background-color: #ff8f00 !important; /* Vibrant Orange/Yellow */
  color: #fff !important;
}
.clue-incorrect {
  background-color: #d32f2f !important; /* Vibrant Red */
  color: #fff !important;
}
/* Add specific style for the N/A year case if needed, otherwise it uses default td */
.guesses-history td:has(span:contains('N/A')) {
   background-color: #3a3a3a !important; /* Ensure it uses default dark bg */
   color: #e0e0e0 !important;
}
/* Target the text spans directly for colors if !important causes issues */
.guesses-history td span {
    display: inline-block; /* Allows padding if needed */
    font-weight: bold;
}
.clue-correct span { color: #fff; }
.clue-near span { color: #fff; }
.clue-incorrect span { color: #fff; }


/* Win/Loss Message Styling */
.state-message {
  margin-top: 30px;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
}

.win-message {
  background-color: #1e4620; /* Dark green background */
  border: 1px solid #2a602d;
  color: #d4edda; /* Light green text */
}
.win-message h2 { color: #d4edda; }

.loss-message {
  background-color: #5a1e21; /* Dark red background */
  border: 1px solid #8e353a;
  color: #ff8a80; /* Lighter red text */
}
.loss-message h2 { color: #ff8a80; }

.state-message a {
  color: #80bdff; /* Lighter blue link */
  font-weight: bold;
  text-decoration: none;
}

.state-message a:hover {
  text-decoration: underline;
}

/* Stats & Share Section */
.stats-share-section {
    margin-top: 30px;
    padding: 20px;
    background-color: #333; /* Match quote background */
    border: 1px solid #444;
    border-radius: 8px;
}

.stats-summary {
    display: flex;
    justify-content: space-around;
    text-align: center;
    margin-bottom: 20px;
    flex-wrap: wrap; /* Allow wrapping on smaller screens */
    gap: 10px;
}

.stat-value {
    font-size: 1.5em;
    font-weight: bold;
    color: #fff;
}

.stat-label {
    font-size: 0.9em;
    color: #aaa; /* Dim label text */
}

.histogram {
    margin-bottom: 20px;
}

.histogram-row {
    display: flex;
    align-items: center;
    margin-bottom: 5px;
    font-size: 0.9em;
}

.histogram-label {
    width: 20px;
    text-align: right;
    margin-right: 10px;
    font-weight: bold;
    color: #ccc; /* Lighter label */
}

.histogram-bar-container {
    flex-grow: 1;
    background-color: #444; /* Match input bg */
    border-radius: 3px;
    height: 20px;
    display: flex;
    align-items: center;
}

.histogram-bar {
    background-color: #777; /* Neutral grey bar */
    height: 100%;
    border-radius: 3px;
    color: #fff; /* White text on bar */
    font-weight: bold;
    font-size: 0.8em;
    padding: 0 5px;
    box-sizing: border-box;
    text-align: right;
    white-space: nowrap;
    overflow: hidden;
    transition: width 0.5s ease-in-out;
    min-width: 20px; /* Make sure bar is slightly visible */
    display: flex;
    justify-content: flex-end;
    align-items: center;
}

.histogram-bar.loss-bar {
    background-color: #d32f2f; /* Match incorrect clue color */
    color: #fff;
}


.share-button {
    display: block;
    margin: 20px auto 0;
    padding: 10px 20px;
    font-size: 1.1em;
    cursor: pointer;
    background-color: #555; /* Match button style */
    color: #e0e0e0;
    border: 1px solid #666;
    border-radius: 4px;
    transition: background-color 0.2s ease;
}

.share-button:hover {
    background-color: #666; /* Match button hover */
}


/* Credits */
.credits {
    text-align: center;
    margin-top: 30px;
    font-size: 0.9em;
    color: #fff; /* Dimmer credits text */
    background-color: #333333AA; /* Match input bg */
}

.credits p {
    margin: 5px 0;
}

.credits a {
    color: #80bdff; /* Link color */
    text-decoration: none;
}

.credits a:hover {
    text-decoration: underline;
}

.error-message {
    color: #ff8a80;
    font-weight: bold;
    text-align: center;
    margin-top: 20px;
    background-color: #5a1e21;
    padding: 10px;
    border-radius: 4px;
    border: 1px solid #8e353a;
}

/* Responsive Adjustments */
@media (max-width: 600px) {
    .guess-area {
        flex-direction: column;
        align-items: stretch;
    }
    /* Keep button visible on mobile but full width */
    .guess-area button {
        width: 100%;
        margin-top: 10px; /* More space when stacked */
       /* display: none; /* Uncomment if you prefer hiding it */
    }
    .guesses-remaining-mobile {
        display: block; /* Show remaining guesses text */
        font-size: 0.85em;
        color: #999;
    }
    .guesses-history th,
    .guesses-history td {
        padding: 6px 8px;
        font-size: 0.9em;
    }
    .stats-summary {
        gap: 15px; /* Ensure wrapping looks okay */
    }
    .stat-value {
        font-size: 1.3em;
    }
    .joedle-container {
        padding: 15px;
        margin: 10px;
    }
}

</style>