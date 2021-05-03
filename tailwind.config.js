const colors = require('tailwindcss/colors')

module.exports = {
    purge: [
      'cafeteria/forms.py',
      'templates/**/*.html',
      'transactions/forms.py'
    ],
    theme: {
      extend: {
        colors: {
            cyan: colors.cyan,
            orange: colors.orange,
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