import { ref, watch } from 'vue'

const THEME_KEY = 'app-theme'

const isDark = ref(localStorage.getItem(THEME_KEY) !== 'light')

function applyTheme(dark: boolean) {
  document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light')
  localStorage.setItem(THEME_KEY, dark ? 'dark' : 'light')
}

// Apply on init
applyTheme(isDark.value)

// Watch for changes
watch(isDark, applyTheme)

export function useTheme() {
  function toggle() {
    isDark.value = !isDark.value
  }

  function setDark() {
    isDark.value = true
  }

  function setLight() {
    isDark.value = false
  }

  return {
    isDark,
    toggle,
    setDark,
    setLight,
  }
}
