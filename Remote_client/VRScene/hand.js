var hand;
var ffinger_2_2;
var finger_2;
var finger_1;
var finger_3_3
var finger_4_4
var finger_5_5;
var finger_3;
var finger_4;
var finger_5;
var big_hand;

var inithand = function() {

    var cube = new THREE.BoxGeometry(2, 2, 0.2);
    //cube.translate(0, 2, 0);
    var sq2 = new THREE.BoxGeometry(0.3, 1.25, 0.2);
    sq2.translate(0, 1.25/2, 0);
    var sq1 = new THREE.BoxGeometry(0.3, 1, 0.2);
    sq1.translate(0, 1/2, 0);
	 var sq4 = new THREE.BoxGeometry(0.3, 1.25*1.1, 0.2);
    sq4.translate(0, 1.25*1.1/2, 0);
    var sq3 = new THREE.BoxGeometry(0.3, 1*1.1, 0.2);
    sq3.translate(0, 1*1.1/2, 0);
    var sq6 = new THREE.BoxGeometry(0.3, 1.25, 0.2);
    sq6.translate(0, 1.25/2, 0);
    var sq5 = new THREE.BoxGeometry(0.3, 1, 0.2);
    sq5.translate(0, 1/2, 0);
	 var sq8 = new THREE.BoxGeometry(0.3, 1.25*0.75, 0.2);
    sq8.translate(0, 1.25*0.75/2, 0);
    var sq7 = new THREE.BoxGeometry(0.3, 1*0.75, 0.2);
    sq7.translate(0, 1*0.75/2, 0);
    var sq9 = new THREE.BoxGeometry(0.3, 1.7, 0.2);
    sq9.translate(0, 1.7/2, 0);

    var material1 = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
    var material2 = new THREE.MeshBasicMaterial({ color: 0xffffe0 });
    var material3 = new THREE.MeshBasicMaterial({ color: 0xff0000 });

    var palm = new THREE.Mesh(cube, material1);

    var finger_2_1 = new THREE.Mesh(sq1, material2);
    var finger_2_2 = new THREE.Mesh(sq2, material3);
    var finger_3_1 = new THREE.Mesh(sq3, material2);
    var finger_3_2 = new THREE.Mesh(sq4, material3);
    var finger_4_1 = new THREE.Mesh(sq5, material2);
    var finger_4_2 = new THREE.Mesh(sq6, material3);
    var finger_5_1 = new THREE.Mesh(sq7, material2);
    var finger_5_2 = new THREE.Mesh(sq8, material3);
    finger_1 = new THREE.Mesh(sq9, material3);

	 var ffinger_1 = new THREE.Object3D();
	 ffinger_1.add(finger_1);
	 ffinger_1.rotateZ(-Math.PI/2);
	 ffinger_1.translateY(1);	 
	 ffinger_1.translateX(0.85);
    hand = new THREE.Object3D();
    finger_2 = new THREE.Object3D();
    ffinger_2_2 = new THREE.Object3D();
    finger_3 = new THREE.Object3D();
    ffinger_3_2 = new THREE.Object3D();
	 finger_4 = new THREE.Object3D();
    ffinger_4_2 = new THREE.Object3D();
	 finger_5 = new THREE.Object3D();
    ffinger_5_2 = new THREE.Object3D();
    ffinger_2_2.add(finger_2_2);
    ffinger_3_2.add(finger_3_2);
    ffinger_4_2.add(finger_4_2);
    ffinger_5_2.add(finger_5_2);
    ffinger_2_2.translateY(1);
    ffinger_3_2.translateY(1*1.1);
	 ffinger_4_2.translateY(1);
	 ffinger_5_2.translateY(1*0.75);
    finger_2.add(ffinger_2_2);
    finger_2.add(finger_2_1);
    finger_3.add(ffinger_3_2);
    finger_3.add(finger_3_1);
    finger_4.add(ffinger_4_2);
    finger_4.add(finger_4_1);
    finger_5.add(ffinger_5_2);
    finger_5.add(finger_5_1);
    finger_2.translateY(1);
    finger_3.translateY(1);
    finger_5.translateY(1);
    finger_4.translateY(1);
    finger_2.translateX(1.7/2);
    finger_3.translateX(0.5/2);
    finger_4.translateX(-0.6/2);
    finger_5.translateX(-1.7/2);

    hand.add(palm);
    hand.add(finger_2);
    hand.add(finger_3);
	 hand.add(finger_4);
	 hand.add(finger_5);
	 hand.add(ffinger_1);
	 big_hand = new THREE.Object3D();
	 big_hand.add(hand);
}