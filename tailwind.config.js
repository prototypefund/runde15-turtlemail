/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./src/**/*.{js,ts,jsx,tsx,vue}",
    "./turtlemail/**/*.{html,jinja,js,py}",
  ],
  theme: {},
  plugins: [require("daisyui")],
  daisyui: {
    darkTheme: "turtlemail",
    themes: [
      {
        turtlemail: {
          ...require("daisyui/src/theming/themes")["cupcake"],
          success: "rgb(59,103,59)",
          primary: "rgb(59,103,59)",
          secondary: "rgb(255,141,0)",
          accent: "oklch(59.48% 0.2069 29.12)",
        },
      },
    ],
  },
};
