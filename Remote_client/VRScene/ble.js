var handAngle = [0, 0, 0];

var handPosition = [0, 0, 0];

var fingerAngle = [0, 0, 0, 0, 0];

function ble_init() {
	var promise = navigator.bluetooth.requestDevice({ filters: [{ services: [0x12ab] }] })
	.then(device => device.gatt.connect())
	.then(server => server.getPrimaryService(0x12ab))
	.then(service => service.getCharacteristic(0x34cd))
	console.log(promise)
	promise.then(characteristic => {
		return characteristic.startNotifications()
  			.then(_ => {
  				console.log("Noti started!")
  				window.removeEventListener("click", ble_init);
 				characteristic.addEventListener('characteristicvaluechanged', handleCharacteristicValueChanged);
 				three_init();
  			});
	})
	.catch(error => { console.log(error); });
}

window.addEventListener('click', ble_init);

function handleCharacteristicValueChanged(event) {
  			var bu = event.target.value;
  			var ta = new Uint8Array(bu.buffer)
  			for (let i=0; i<5; i++) {
				fingerAngle[i] = ta[i];   			
  			}
  			ta = new Int16Array(ta.buffer)
  			for (let i=0; i<3; i++) {
  				handPosition[i] = ta[i+3];
  			}
  			for (let i=0; i<3; i++) {
  				handAngle[i] = ta[i+6];
  			}
}
