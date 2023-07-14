const year = document.getElementById("year");
if (year) year.textContent = new Date().getFullYear();

const relevant = function (query, link) {
  fetch("/relevant", {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      query: query,
      link: link,
    }),
  });
};
