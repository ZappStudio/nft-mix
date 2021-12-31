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
      this.getContract()
    },
    async getContract() {
      try {
        const contractPath = '../../solidity/build/contracts/AnimalPoker.json'
        const response = await fetch(contractPath)
        const data = await response.json()
        const netId = await web3.eth.net.getId()
        const deployedNetwork = data.networks[netId]
        this.contract = new web3.eth.Contract(
          data.abi,
          deployedNetwork && deployedNetwork.address
        )

        console.log("Inicializando escuchador eventos")
        let transferEvent = this.contract.Transferred({}, {fromBlock: 0, toBlock: 'latest'})
        transferEvent.get((error, logs) => {
          // we have the logs, now print them
          logs.forEach(log => console.log(log.args))
        })
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
    <vue-metamask userMessage="msg" @onComplete="onComplete"/>
    <button
      v-if="web3"
      @click="getContract"
      class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
    >
      Hola soy un botón que mintea
    </button>
  </div>
</template>
