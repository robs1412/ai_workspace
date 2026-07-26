const prompts = [
  "Act as a patient tutor. Explain what a local web server is to a beginner in 5 bullets, then give one Mac command to try.",
  "Rewrite this messy note into a clear checklist. Ask up to 3 questions first if important facts are missing.",
  "Review my agent prompt for risk. Point out unclear scope, missing verification, and anything that could cause unwanted file changes.",
  "Create a 30-minute practice plan for learning GitHub Desktop, Codex, and a local web server. Keep it beginner-friendly.",
  "Compare chat, app assistant, coding agent, loop, harness, and server in a table with one example each."
];

const button = document.querySelector("#prompt-button");
const output = document.querySelector("#prompt-output");

button.addEventListener("click", () => {
  const index = Math.floor(Math.random() * prompts.length);
  output.textContent = prompts[index];
});
