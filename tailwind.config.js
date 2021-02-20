const colors = require('tailwindcss/colors')

module.exports = {
    purge: ['templates/**/*.html'],
    theme: {
      extend: {
        colors: {
            cyan: colors.cyan,
          },
        fontFamily: {
            sans: ['Inter var',],
        },
      },
    },
    variants: {},
    plugins: [
        require('@tailwindcss/forms'),
    ],
  }