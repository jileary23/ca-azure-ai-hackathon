/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        lacounty: {
          blue: "#003366",
          gold: "#c9a84c",
          lightblue: "#1a4d8f",
        },
      },
    },
  },
  plugins: [],
};
