<template>
  <div class="brand-logo" :class="[`brand-logo--${size}`, { 'brand-logo--mark-only': markOnly }]">
    <svg class="brand-mark" viewBox="0 0 64 64" role="img" aria-label="水木学堂">
      <defs>
        <linearGradient id="shuimuLeaf" x1="10" y1="10" x2="54" y2="54" gradientUnits="userSpaceOnUse">
          <stop offset="0" stop-color="#38bdf8" />
          <stop offset="1" stop-color="#22c55e" />
        </linearGradient>
        <linearGradient id="shuimuWater" x1="12" y1="40" x2="52" y2="56" gradientUnits="userSpaceOnUse">
          <stop offset="0" stop-color="#0ea5e9" />
          <stop offset="1" stop-color="#1e5b7a" />
        </linearGradient>
      </defs>
      <path class="leaf left" d="M31 12C22 13 15 18 12 26c8 1 16-1 22-8 1-2 0-5-3-6Z" />
      <path class="leaf right" d="M33 12c9 1 16 6 19 14-8 1-16-1-22-8-1-2 0-5 3-6Z" />
      <path class="trunk" d="M32 18v25M20 28h24M24 36c4-2 6-5 8-9 2 4 4 7 8 9" />
      <path class="water-line" d="M16 48c5-5 10-5 16 0s11 5 16 0" />
      <circle class="drop" cx="22" cy="54" r="3" />
      <circle class="drop" cx="32" cy="56" r="3" />
      <circle class="drop" cx="42" cy="54" r="3" />
    </svg>
    <span v-if="!markOnly" class="brand-text">
      <strong>水木学堂</strong>
      <small v-if="showSubtitle">在线教育平台</small>
    </span>
  </div>
</template>

<script setup>
defineProps({
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value)
  },
  markOnly: {
    type: Boolean,
    default: false
  },
  showSubtitle: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped>
.brand-logo {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  color: #102a43;
  line-height: 1;
}

.brand-mark {
  flex: 0 0 auto;
  filter: drop-shadow(0 8px 16px rgba(14, 165, 233, 0.18));
}

.brand-logo--sm .brand-mark {
  width: 34px;
  height: 34px;
}

.brand-logo--md .brand-mark {
  width: 42px;
  height: 42px;
}

.brand-logo--lg .brand-mark {
  width: 58px;
  height: 58px;
}

.brand-text {
  display: grid;
  gap: 5px;
}

.brand-text strong {
  color: #0f3f57;
  font-size: 18px;
  font-weight: 850;
  letter-spacing: 0.08em;
}

.brand-logo--lg .brand-text strong {
  font-size: 28px;
}

.brand-text small {
  color: #3b7188;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.18em;
}

.brand-logo--mark-only {
  gap: 0;
}

.leaf {
  fill: url("#shuimuLeaf");
}

.leaf.right {
  opacity: 0.9;
}

.trunk {
  fill: none;
  stroke: #14532d;
  stroke-width: 4;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.water-line {
  fill: none;
  stroke: url("#shuimuWater");
  stroke-width: 4;
  stroke-linecap: round;
}

.drop {
  fill: #0ea5e9;
}
</style>
