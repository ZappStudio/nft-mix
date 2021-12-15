<script>
import AppHeader from "../components/layout/app-header";
import AppFooter from "../components/layout/app-footer";

export default {
  name: "default",
  components: {AppFooter, AppHeader}
}
</script>

<template>
  <div>
    <app-header />
    <nuxt />
    <app-footer />
  </div>
</template>


