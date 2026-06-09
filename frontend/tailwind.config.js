/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        pitch: "#0f6b3f",
        ink: "#172033",
        ocean: "#174ea6",
        line: "#d6deea"
      }
    }
  },
  plugins: []
};
