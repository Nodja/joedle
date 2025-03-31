<template>
  <div class="joedle-container">
    <h1>Joedle</h1>
    <p>Guess which Joseph Anderson video/stream the quote is from!</p>

    <div v-if="isLoading">Loading today's quote...</div>
    <div v-else-if="!solution">
      <p class="error-message">Could not find a quote for today ({{ todayKey }}). Please check quotes.json.</p>
    </div>
    <div v-else>
      <!-- Quote Display -->
      <blockquote class="quote-display">
        "{{ quoteDisplay }}"
      </blockquote>

      <!-- Guess Input & Autocomplete -->
      <div class="guess-area" v-if="!isWon">
        <div class="autocomplete-wrapper">
          <input
            type="text"
            v-model="currentGuessInput"
            @input="handleInput"
            @focus="showAutocomplete = true"
            @blur="hideAutocomplete"
            placeholder="Type your guess..."
            :disabled="isWon"
            aria-label="Guess the source"
          />
           <div class="autocomplete-placeholder" v-if="showAutocomplete && !currentGuessInput && !isWon">
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
        <button @click="submitGuess" :disabled="!currentGuessInput || isWon || !isValidGuessFormat">Guess</button>
         <p v-if="currentGuessInput && !isValidGuessFormat && !showAutocomplete" class="input-warning">
            Select a valid option from the list.
         </p>
      </div>

      <!-- Guess History & Clues -->
      <div v-if="reversedGuesses.length > 0" class="guesses-history">
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
              <td :class="getClueClass(guess.yearMatch === 'correct')">
                <span v-if="guess.yearMatch === 'correct'">✅ {{ guess.guessedYear }}</span>
                <span v-else-if="guess.yearMatch === 'higher'">⬇️ Too High ({{ guess.guessedYear }})</span> <!-- Correct year is lower -->
                <span v-else-if="guess.yearMatch === 'lower'">⬆️ Too Low ({{ guess.guessedYear }})</span> <!-- Correct year is higher -->
                <span v-else>N/A</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Win State -->
      <div v-if="isWon" class="win-message">
        <h2>Congratulations! You got it!</h2>
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
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';

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

// --- Lifecycle ---
onMounted(async () => {
  todayKey.value = getTodayKey();
  // *** For Testing: Override todayKey if needed ***
  // todayKey.value = '2025-04-02'; // Example: Uncomment to test with Subnautica quote

  await loadQuotes();
  if (quotesData.value) {
    solution.value = quotesData.value[todayKey.value] || null;
    generateAllOptions();
  }
  isLoading.value = false;
});

// --- Computed Properties ---
const quoteDisplay = computed(() => {
  // Replace [X] placeholder in quotes if needed
  if (solution.value?.quote && solution.value?.game) {
      // Basic placeholder replacement, adjust regex if needed
      return solution.value.quote.replace(/\[X\]/gi, solution.value.game);
  }
  return solution.value?.quote || '';
});


const filteredOptions = computed(() => {
  if (!currentGuessInput.value) {
    return []; // Don't show all options if input is empty
  }
  const searchTerm = currentGuessInput.value.toLowerCase();
  return allPossibleOptions.value.filter(option =>
    option.toLowerCase().includes(searchTerm)
  ).slice(0, 10); // Limit suggestions
});

const reversedGuesses = computed(() => {
  // slice() creates a shallow copy before reversing,
  // preventing modification of the original 'guesses' array
  return guesses.value.slice().reverse();
});

// Check if the current input exactly matches one of the possible options
const isValidGuessFormat = computed(() => {
    return allPossibleOptions.value.includes(currentGuessInput.value);
});


// --- Methods ---
function getTodayKey() {
  const today = new Date();
  const year = today.getFullYear();
  const month = String(today.getMonth() + 1).padStart(2, '0'); // Months are 0-indexed
  const day = String(today.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

async function loadQuotes() {
  try {
    // Assumes quotes.json is in the /public folder
    const response = await fetch('/quotes.json');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    quotesData.value = await response.json();
  } catch (error) {
    console.error("Failed to load quotes:", error);
    quotesData.value = null; // Ensure it's null on error
  }
}

function generateAllOptions() {
    if (!quotesData.value) return;
    allPossibleOptions.value = Object.values(quotesData.value).map(q => `${q.type} - ${q.title}`);
    // Optional: Remove duplicates if somehow titles/types could repeat across dates in source data
    allPossibleOptions.value = [...new Set(allPossibleOptions.value)];
    allPossibleOptions.value.sort(); // Sort alphabetically
}


function handleInput() {
  showAutocomplete.value = true;
}

function hideAutocomplete() {
  // Delay hiding to allow click event on options to register
  setTimeout(() => {
    showAutocomplete.value = false;
  }, 200);
}

function selectOption(option) {
  currentGuessInput.value = option;
  showAutocomplete.value = false; // Hide immediately on selection
  // Optional: Focus the submit button or trigger submit directly
}

function findQuoteDataBySelection(selectionString) {
    if (!quotesData.value || !selectionString) return null;

    // Find the first quote entry that matches the "Type - Title" format
    // This assumes the combination is unique within the dataset loaded.
    for (const key in quotesData.value) {
        const quote = quotesData.value[key];
        if (`${quote.type} - ${quote.title}` === selectionString) {
            return quote;
        }
    }
    return null; // Not found
}


function submitGuess() {
  if (!currentGuessInput.value || isWon.value || !solution.value || !isValidGuessFormat.value) {
      console.warn("Submit blocked:", {
          input: currentGuessInput.value,
          isWon: isWon.value,
          solutionExists: !!solution.value,
          isValid: isValidGuessFormat.value
      });
    return;
  }

  const guessedData = findQuoteDataBySelection(currentGuessInput.value);

  if (!guessedData) {
      console.error("Could not find data for guess:", currentGuessInput.value);
      // Maybe show a user-facing error here?
      return; // Should not happen if isValidGuessFormat is true, but good failsafe
  }

  const guessResult = {
    guessedTitle: currentGuessInput.value, // Store the full "Type - Title" string
    guessedType: guessedData.type,
    guessedGame: guessedData.game,
    guessedYear: guessedData.year,
    typeMatch: guessedData.type === solution.value.type,
    gameMatch: guessedData.game === solution.value.game,
    yearMatch: compareYears(guessedData.year, solution.value.year)
  };

  guesses.value.push(guessResult);

  // Check for win condition (using game AND type AND year for robustness)
   if (guessResult.typeMatch && guessResult.gameMatch && guessResult.yearMatch === 'correct') {
     isWon.value = true;
   }
  // Could also check if guessedData.title === solution.value.title,
  // but the type/game/year check is closer to the clue logic.

  currentGuessInput.value = ''; // Clear input after guess
}

function compareYears(guessedYear, solutionYear) {
  if (guessedYear === solutionYear) return 'correct';
  if (guessedYear < solutionYear) return 'lower'; // Guessed year is lower than solution
  if (guessedYear > solutionYear) return 'higher'; // Guessed year is higher than solution
  return 'unknown'; // Should not happen with valid years
}

// Return 'clue-correct' only if the match is true, otherwise return empty string for neutral background
function getClueClass(isCorrect) {
  return isCorrect ? 'clue-correct' : '';
}

</script>

<style scoped>
/* Dark Theme */
.joedle-container {
  font-family: sans-serif;
  max-width: 700px;
  margin: 20px auto;
  padding: 20px;
  border: 1px solid #555; /* Darker border */
  border-radius: 8px;
  background-color: #2d2d2d; /* Dark background */
  color: #e0e0e0; /* Light text */
}

h1, h2 {
  text-align: center;
  color: #f5f5f5; /* Brighter title text */
}

.quote-display {
  background-color: #424242; /* Slightly lighter dark background */
  border-left: 5px solid #44aaff; /* Adjust border color */
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
  margin-bottom: 20px;
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
  border: 1px solid #666; /* Darker border */
  border-radius: 4px;
  width: 100%;
  box-sizing: border-box;
  background-color: #555; /* Dark input background */
  color: #e0e0e0; /* Light input text */
}

.guess-area input[type="text"]::placeholder {
  color: #aaa; /* Lighter placeholder text */
}

.guess-area button {
  padding: 10px 15px;
  font-size: 1em;
  cursor: pointer;
  background-color: #007bff; /* Keep blue or adjust */
  color: white;
  border: none;
  border-radius: 4px;
  transition: background-color 0.2s ease;
}

.guess-area button:disabled {
  background-color: #555; /* Darker disabled background */
  color: #999;
  cursor: not-allowed;
}

.guess-area button:not(:disabled):hover {
  background-color: #0056b3; /* Darker blue on hover */
}

.input-warning {
    color: #ff8a80; /* Lighter red for dark theme */
    font-size: 0.9em;
    margin-top: 5px;
}

.autocomplete-placeholder {
  position: absolute;
  top: 100%; /* Position below the input */
  left: 0;
  width: calc(100% - 2px); /* Match input width minus borders */
  background-color: #424242; /* Match dropdown background */
  color: #aaa;
  padding: 8px 12px;
  border: 1px solid #666;
  border-top: none;
  box-shadow: 0 4px 6px rgba(0,0,0,0.2);
  border-radius: 0 0 4px 4px;
  z-index: 10;
  font-size: 0.9em;
  font-style: italic;
}


.autocomplete-list {
  list-style: none;
  margin: 0;
  padding: 0;
  border: 1px solid #666; /* Dark border */
  border-top: none;
  max-height: 200px;
  overflow-y: auto;
  background-color: #424242; /* Dark dropdown background */
  color: #e0e0e0; /* Light text */
  position: absolute;
  width: 100%;
  z-index: 10;
  box-shadow: 0 4px 6px rgba(0,0,0,0.2); /* Darker shadow */
  border-radius: 0 0 4px 4px;
}

.autocomplete-list li {
  padding: 8px 12px;
  cursor: pointer;
}

.autocomplete-list li:hover,
.autocomplete-list li:focus {
  background-color: #555; /* Slightly lighter dark background on hover */
  outline: none;
}

.guesses-history {
  margin-top: 30px;
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
}

.guesses-history th {
  background-color: #4f4f4f; /* Slightly different header background */
  font-weight: bold;
  color: #f5f5f5;
}

/* Style for correct clues */
.clue-correct {
  background-color: #1e4620 !important; /* Dark green background - use !important if needed */
  color: #a3d9a5 !important; /* Light green text */
}

/* Incorrect clues will use the default td background (#3a3a3a) */


.win-message {
  margin-top: 30px;
  padding: 20px;
  background-color: #1e4620; /* Dark green background */
  border: 1px solid #2a602d; /* Darker green border */
  border-radius: 8px;
  color: #d4edda; /* Light green text */
  text-align: center;
}

.win-message h2 {
    color: #d4edda;
}

.win-message a {
  color: #80bdff; /* Lighter blue link for dark theme */
  font-weight: bold;
  text-decoration: none;
}

.win-message a:hover {
  text-decoration: underline;
}

.error-message {
    color: #ff8a80; /* Lighter red error text */
    font-weight: bold;
    text-align: center;
    margin-top: 20px;
    background-color: #5a1e21; /* Dark red background */
    padding: 10px;
    border-radius: 4px;
    border: 1px solid #8e353a;
}
</style>