
function confirmAction() {
    return {
        show: false,
        itemID: '',
        open(itemID, name) { 
          this.show = true
          this.itemID = itemID
          document.getElementById("item-name").innerHTML = name
        },
        cancel() {
          this.show = false
          this.itemID = ''
        },
        confirm() {
          document.getElementById("item-id").value = this.itemID
          this.show = false
        },
        isOpen() {
          return this.show === true
        },
    }
}
