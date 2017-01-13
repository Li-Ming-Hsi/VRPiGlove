var five = require("johnny-five");
var board = new five.Board();
var net = require("net")
var bleno = require("bleno")
var socketFile = "../communicate.sock"

var unixClient = new net.Socket();

var establishConnect = function() {
	unixClient.connect({path: socketFile});	
}

var tryUntilSuccess = setInterval(establishConnect, 1000)

var hand_angle = [0, 0, 0]

var position = [0, 0, 0]

var finger_angle = [0, 0, 0, 0, 0];

board.on("ready", function() {
	//var gyro = new five.Gyro({
	//	controller: "MPU6050",
	//	sensitivity: 131	
	//});
	
	var flex1 = new five.Sensor({pin:"A0", freq:30});
	var flex2 = new five.Sensor({pin:"A1", freq:30});
	var flex3 = new five.Sensor({pin:"A2", freq:30});
	var flex4 = new five.Sensor({pin:"A3", freq:30});
	//var flex5 = new five.Sensor({pin:"A4", freq:30});

	var gyro = new five.Gyro({
		controller: "MPU6050"
	});

   flex1.on("data", function(value) {
		//console.log(value);
      finger_angle[0] = valueMap(-740, -660, 0, 90, -value);
      //console.log(finger_angle)
   });
   
   flex2.on("data", function(value) {
		//console.log(value);
      finger_angle[1] = valueMap(-740, -600, 0, 180, -value);
      //console.log(finger_angle)
   });
   
	flex3.on("data", function(value) {
		//console.log(value);
      finger_angle[2] = valueMap(-740, -570, 0, 180, -value);
      //console.log(finger_angle)
   });
   
	flex4.on("data", function(value) {
		//console.log(value);
      finger_angle[3] = valueMap(-600, -350, 0, 180, -value);
	finger_angle[4] = finger_angle[3];
      //console.log(finger_angle)
   });
   
	//flex5.on("data", function(value) {
		//console.log(value);
      //finger_angle[4] = valueMap(-600, -350, 0, 180, -value);
      //console.log(finger_angle)
   //});
	
	gyro.on("change", function() {
		hand_angle = [this.pitch.angle, this.roll.angle, this.yaw.angle];
		//console.log(hand_angle)
		//console.log("pitch: ", this.pitch);
		//console.log("roll: ", this.roll);
		//console.log("yaw ", this.yaw);
	});
});

var valueMap = function(x, y, nx, ny, value) {
    if(value > y) { value = y }
    else if(value < x) { value = x }
    return (value - x) / (y - x) * (ny - nx) + nx
}

var hand_calibration = function(value) {
	return value
}

bleno.on('stateChange', function(state) {
    console.log('State change: ' + state);
    if (state === 'poweredOn') {
        bleno.startAdvertising('MyDevice',['12ab']);
    } else {
        bleno.stopAdvertising();
    }
});

bleno.on('accept', function(clientAddress) {
	console.log("Accepted connection from address: " + clientAddress);
});

bleno.on('disconnect', function(clientAddress) {
	console.log("Disconnected from address: " + clientAddress);
});

bleno.on('advertisingStart', function(error) {
	if (error) {
		console.log("Advertising start error:" + error);
	} else {
		console.log("Advertising start success");
		bleno.setServices([
			new bleno.PrimaryService({
 				uuid: '12ab',
 				characteristics : [
  					new bleno.Characteristic({
						value: null,
						uuid: '34cd',
						properties: ['notify'],
						onSubscribe: function(maxValueSize, updateValueCallback) {
 							console.log("Device subscribed");
 							this.intervalId = setInterval(function() {
  								var data_a = new ArrayBuffer(maxValueSize);
  								var data_t = new Uint8Array(data_a);
  								for (let i=0; i<5; i++) {
									data_t[i] = finger_angle[i];  								
  								}
  								data_t = new Int16Array(data_t.buffer);
  								for (let i=0; i<3; i++) {
									data_t[i+3] = position[i]  								
  								}
  								for (let i=0; i<3; i++) {
									data_t[i+6] = hand_angle[i]  								
  								}
								data_t = new Uint8Array(data_t.buffer)
  								for (let i=0; i<maxValueSize; i++) {
  									data_a[i] = data_t[i]
  								}
  								var trans = Buffer.from(data_a);
  								updateValueCallback(trans);
 							}, 30);
						},
						onUnsubscribe: function() {
 							console.log("Device unsubscribed");
 							clearInterval(this.intervalId);
						}
					})
				]
			})
		]);
	}
});

var resetToNullPos = function() {
	//console.log("set to Null")
}


unixClient
	.on("connect", function() {
		console.log("unix socket connected!");
		clearInterval(tryUntilSuccess);	
	})
	.on("data", function (data) {
		console.log(data)
		var receive = data.toString();
		if(receive === "None detected") {
			resetToNullPos()
		} else {
			//console.log(data.length)
			var temp8 = new Uint8Array(data)
			var temp32 = new Float32Array(temp8.buffer)
			position[0] = 160 - Math.round(temp32[0])
			position[1] = 120 - Math.round(temp32[1])
			console.log(position[0], position[1])
		}
		unixClient.write("ACK");
  	})
  	.on('error', function (err) {
		console.log(err);
	})
	.on('end', function () {
		console.log("client disconnected");
});

