<script>
export default {
  name: 'IndexPage',
  data() {
    return {
      web3: null,
      contact: null,
      msg: 'This is demo net work',
    }
  },
  methods: {
    onComplete(data) {
      this.web3 = data
    },
    async getContract() {
      try {
        const contractPath = '../../solidity/contracts/test_contracts/test.json'
        const response = await fetch(contractPath)
        const data = await response.json()
        const netId = await web3.eth.net.getId()
        const deployedNetwork = data.networks[netId]
        this.contract = new web3.eth.Contract(
          data.abi,
          deployedNetwork && deployedNetwork.address
        )
        return contract
      } catch (e) {
        console.log(e)
      }
    },
  },
}
</script>

<template>
  <div id="demo">
    <vue-metamask userMessage="msg" @onComplete="onComplete" />
    <button
      v-if="web3"
      @click="getContract"
      class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
    >
      Hola soy un botón que mintea
    </button>
  </div>
</template>
