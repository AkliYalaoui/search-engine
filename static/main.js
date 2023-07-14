const year = document.getElementById("year");
if (year) year.textContent = new Date().getFullYear();

// Autocomplete functionality
document.addEventListener("DOMContentLoaded", function () {
  const autocompleteItems = document.getElementById("autocomplete-items");
  const queryInput = document.querySelector(".query-input");

  // Event listener for input changes
  queryInput.addEventListener("input", function () {
    const query = this.value.trim();

    // Make AJAX request to fetch autocomplete suggestions
    fetch("/autocomplete", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: "query=" + encodeURIComponent(query),
    })
      .then((response) => response.json())
      .then((data) => {
        displayAutocompleteSuggestions(data.suggestions);
      })
      .catch((error) => {
        console.error(error);
      });
  });

  // Display autocomplete suggestions
  function displayAutocompleteSuggestions(suggestions) {
    autocompleteItems.innerHTML = "";

    if (suggestions.length > 0) {
      suggestions.forEach((suggestion) => {
        const item = document.createElement("div");
        item.textContent = suggestion;
        item.addEventListener("click", function () {
          queryInput.value = suggestion;
          autocompleteItems.innerHTML = "";
        });
        autocompleteItems.appendChild(item);
      });
    } else {
      autocompleteItems.innerHTML = "<div>No suggestions found.</div>";
    }
  }
});
