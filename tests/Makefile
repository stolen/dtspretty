test: test-mini-sample


test-mini-sample:
	dtc -I dts -O dtb -@ mini-sample.dts -o mini-sample.dtb
	dtc -I dtb -O dts mini-sample.dtb -o mini-sample-decompiled.dts
	../dtspretty.py -r mini-rules.yaml mini-sample-decompiled.dts > mini-sample-restored.dts
	dtc -I dts -O dtb -@ mini-sample-restored.dts -o mini-sample-rebuilt.dtb
	dtc -I dtb -O dts mini-sample-rebuilt.dtb -o mini-sample-rebuilt.dts
	cmp -s mini-sample-decompiled.dts mini-sample-rebuilt.dts
