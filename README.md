# /pub/svc/commerce/gobilda

goBILDA online store.

This package can be used for cost estimates for assemblies that use goBILDA parts.
Placing orders is not implemented yet.

The goBILDA parts themselves are defined in [/pub/robotics/parts/gobilda](https://github.com/openvmp/partcad-robotics-part-vendor-gobilda).


## Usage
Get an estimate for [an assembly from the OpenVMP robot](https://partcad.org/repository/package/robotics/multimodal/openvmp/robots/don1):

```shell
$ pc supply quote --provider gobilda /pub/robotics/multimodal/openvmp/robots/don1:assembly-wormgear
INFO:  DONE: InitCtx: /Users/clairbee/projects/robotics/provider-gobilda: 0.00s
INFO:  The following quotes are received:
INFO:  		/pub/svc/commerce/gobilda:gobilda: 525aea14-5383-490c-a73e-5cfc0099baa0: $51.84
INFO:  			/pub/robotics/parts/gobilda:motion/worm_gear_28t#1
INFO:  			/pub/robotics/parts/gobilda:hardware/spacer_plastic_8mm_1mm#3
INFO:  			/pub/robotics/parts/gobilda:motion/worm_8mmREX#1
INFO:  			/pub/robotics/parts/gobilda:hardware/spacer_steel_8mm_4mm#1
INFO:  			/pub/robotics/parts/gobilda:motion/bearing_flanged_8mmREX#2
INFO:  			/pub/robotics/parts/gobilda:motion/hub_sonic_8mmREX#1
...
```


<br/><br/>

*Generated by [PartCAD](https://partcad.org/)*