# Changelog

<!--next-version-placeholder-->

## v0.10.4 (2024-01-16)

### Fix

* Refactor to use websocket ([`c1e7f45`](https://github.com/Lash-L/anova_wifi/commit/c1e7f45b2a8f8b6f266825317d63e58f34498831))

## v0.10.3 (2023-06-07)
### Fix
* Set temperature unit ([`70325b0`](https://github.com/Lash-L/anova_wifi/commit/70325b0b67a751bd775e98fdcd23ae5b3a106ad8))

## v0.10.2 (2023-06-07)
### Fix
* Correctly update mode ([`5ad6c99`](https://github.com/Lash-L/anova_wifi/commit/5ad6c99170d84706e8fd572600611ca9ffdb62ba))

## v0.10.1 (2023-05-07)
### Fix
* Mypy error ([`c99cab0`](https://github.com/Lash-L/anova_wifi/commit/c99cab03975eb0e38ae92babf8681475a06c6809))
* Only update if 15 seconds have passed ([`303e791`](https://github.com/Lash-L/anova_wifi/commit/303e791f9dd888b8b5b36788cbb77b20d7a8097d))

## v0.10.0 (2023-05-05)
### Feature
* Add debug to ws ([`dcdeb97`](https://github.com/Lash-L/anova_wifi/commit/dcdeb97d3034b3cff18268b15227380717e54f0d))

## v0.9.0 (2023-04-28)
### Feature
* Changed to dataclass for updates ([`4394c5d`](https://github.com/Lash-L/anova_wifi/commit/4394c5df40796053c8e0f60b6c408e42aa039ba7))

### Fix
* Linting ([`8657c1d`](https://github.com/Lash-L/anova_wifi/commit/8657c1d4b7e338f5f82ec5acef62bb52f07f779f))

## v0.8.0 (2023-04-21)
### Feature
* Ignore already existing devices ([`c7c7861`](https://github.com/Lash-L/anova_wifi/commit/c7c7861d8d05f85274451c84b0c386e5885b6446))

## v0.7.0 (2023-04-21)
### Feature
* Add typeddict for anova updated ([`7f2da00`](https://github.com/Lash-L/anova_wifi/commit/7f2da00d84750bc9168b13184936a609db15cdd6))

## v0.6.2 (2023-04-04)
### Fix
* Set water temp as None if it does not exist ([`2750a9d`](https://github.com/Lash-L/anova_wifi/commit/2750a9d83b8af30365a92e1af01040b532ae1ecf))

## v0.6.1 (2023-03-29)
### Fix
* Add limitation to ws url ([`9f2ce32`](https://github.com/Lash-L/anova_wifi/commit/9f2ce326bb3869755f96acbe8949dadff0ff2d63))

## v0.6.0 (2023-03-28)
### Feature
* Add logging and dependabot ([`e994723`](https://github.com/Lash-L/anova_wifi/commit/e994723ace5bfcd45b4559034a732ae42d073e32))
* Added logging and dependabot ([`a75c853`](https://github.com/Lash-L/anova_wifi/commit/a75c853278dabadfb4843f9bdddff010ed2f7731))

## v0.5.2 (2023-03-17)
### Fix
* Bump sensor-state-data ([`f79c3a1`](https://github.com/Lash-L/anova_wifi/commit/f79c3a1ea92af90f4f28a2f9ab45b43ce882d9f8))

## v0.5.1 (2023-03-17)
### Fix
* Improved request to sous vide ([`39c5c4a`](https://github.com/Lash-L/anova_wifi/commit/39c5c4a51fda947d5b390ccb6f62459367eb4039))

## v0.5.0 (2023-03-17)
### Feature
* Added new binary sensors ([`d5d6bf1`](https://github.com/Lash-L/anova_wifi/commit/d5d6bf109c7fb9705a71250ae10270264c3e783c))

## v0.4.3 (2023-03-15)
### Fix
* Bump poetry lock ([`74c570d`](https://github.com/Lash-L/anova_wifi/commit/74c570dc4f555f2bf2dec6dcd6292412da26c8f5))
* Change to strenum ([`9527641`](https://github.com/Lash-L/anova_wifi/commit/952764197b60a6400c8ae70a551da03068bf966e))

## v0.4.2 (2023-03-15)
### Fix
* Add no devices found to init ([`4436113`](https://github.com/Lash-L/anova_wifi/commit/4436113550cae42d094587a8d5a31a247bc5fb6f))
* Added timeout for getting devices ([`5671d3f`](https://github.com/Lash-L/anova_wifi/commit/5671d3f825a8474c1daef1a967abd8ab2b804d46))

## v0.4.1 (2023-03-15)
### Fix
* Make api jwt public ([`ecc1a82`](https://github.com/Lash-L/anova_wifi/commit/ecc1a8275119f078129f1d5279b22b38aaefaf9a))
* Make jwt public ([`0e237ab`](https://github.com/Lash-L/anova_wifi/commit/0e237ab8c6a6840a35635e3cbbb5e8de5d5f4f9e))

## v0.4.0 (2023-03-15)
### Feature
* Add authentication ([`d0e4976`](https://github.com/Lash-L/anova_wifi/commit/d0e49760707460319054d082104bfcae648d80a1))

### Fix
* Py 3.9 ([`9145fc5`](https://github.com/Lash-L/anova_wifi/commit/9145fc5e6a794238032a8b1359af863bb863cf72))

## v0.3.1 (2023-02-22)
### Fix
* Session tests ([`e0d0f7c`](https://github.com/Lash-L/anova_wifi/commit/e0d0f7cf1f8c848b8579d741be3570741bd065c2))
* Repaired session getting closed ([`c8af5ea`](https://github.com/Lash-L/anova_wifi/commit/c8af5ea3a882d8f127bceac6a0f56ab5b19a7e83))

## v0.3.0 (2023-02-21)
### Feature
* Added support for passing clientsession ([`d834ec9`](https://github.com/Lash-L/anova_wifi/commit/d834ec97340fcef9df24f317a212d91380013bfb))

### Fix
* Bump semantic release ([`c98a71a`](https://github.com/Lash-L/anova_wifi/commit/c98a71a4bc110b9b241bb82698534bc225d6cbb5))

## v0.2.7 (2023-01-29)
### Fix
* Removed "nxp" from system info key options ([`b7c5a64`](https://github.com/Lash-L/anova_wifi/commit/b7c5a648fbb87746d85cd83cc3fb57e09fb081b3))

## v0.2.6 (2023-01-29)
### Fix
* Updated isort ([`f104362`](https://github.com/Lash-L/anova_wifi/commit/f1043629d74b0340792557494d11ed13dd0f2ecb))
* Pre commit ([`798f44b`](https://github.com/Lash-L/anova_wifi/commit/798f44bdeea081dd728502d8385dad167acc4379))
* Poetry version issue ([`b9813a2`](https://github.com/Lash-L/anova_wifi/commit/b9813a2f9cf1487511213cd56aeecb6bd11b0cd2))
* Added support for an500-us00 ([`b555b8b`](https://github.com/Lash-L/anova_wifi/commit/b555b8b1905b0b31ad6908da116faae316d5ad44))

## v0.2.5 (2023-01-20)
### Fix
* Added low water mode ([`3c755d2`](https://github.com/conway220/anova_wifi/commit/3c755d21fca546f866d91d8f1a668588192725c7))
* Made state and mode go to map ([`48cbe07`](https://github.com/conway220/anova_wifi/commit/48cbe07958f51a228a120ca0be160489a26e7fd5))

## v0.2.4 (2023-01-19)
### Fix
* Removed unused types-requests ([`5e62cae`](https://github.com/conway220/anova_wifi/commit/5e62cae32fbb0c6c0e7d092174762f387551eb01))

## v0.2.3 (2023-01-19)
### Fix
* Added export for error ([`e4b2c32`](https://github.com/conway220/anova_wifi/commit/e4b2c3293db39184d4d944da9b8510131163ae6c))

## v0.2.2 (2023-01-19)
### Fix
* Removed unneeded asyncio import ([`da2f2e0`](https://github.com/conway220/anova_wifi/commit/da2f2e0124aacd7bef48cd473c123a4330ee5534))
* Remove stale asyncio run ([`8a11635`](https://github.com/conway220/anova_wifi/commit/8a116357fccfea2c1cdd7b4eaba9a04891c22632))

## v0.2.1 (2023-01-19)
### Fix
* Pytest-asyncio dependency issue ([`b80d9dd`](https://github.com/conway220/anova_wifi/commit/b80d9dd23e8a05137ef263bb2db488698dcb9ec8))
* Aiohttp dependency issue ([`171ddfd`](https://github.com/conway220/anova_wifi/commit/171ddfd5d5f54c9d2e497908bdd91e1e07b1db72))

## v0.2.0 (2023-01-19)
### Feature
* Simplified and reworked parser ([`894f97f`](https://github.com/conway220/anova_wifi/commit/894f97fb63fc4bc5f77ac91037142e32680185ff))

### Fix
* Idea files pre-commit ([`a9e5b5d`](https://github.com/conway220/anova_wifi/commit/a9e5b5d16b05e5c5e8a4e790eece76b1f2a2bc56))
* Resolved pre-commit issues ([`e0c22e6`](https://github.com/conway220/anova_wifi/commit/e0c22e6415a85e9048e7c2a481c8a600df30a5a4))

## v0.1.2 (2023-01-18)
### Fix
* Changing requests version for HA ([`ac36315`](https://github.com/conway220/anova_wifi/commit/ac36315fc4239b9816ca244d66c267434f703bd5))

## v0.1.1 (2023-01-18)
### Fix
* Moved device_key to start_update ([`1dddd7f`](https://github.com/conway220/anova_wifi/commit/1dddd7fc80b8d915df71f4c9bd4bd322647ff811))

## v0.1.0 (2023-01-18)
### Feature
* Added test for parser ([`509a45b`](https://github.com/conway220/anova_wifi/commit/509a45b2b382af55b8296794bfb9f2e9320e8d57))

### Fix
* Removed unneeded python-versions ([`df8d522`](https://github.com/conway220/anova_wifi/commit/df8d522c3a4c85d36ed425aca0d5e79b9806db61))

### Documentation
* Add @conway220 as a contributor ([`ce956a2`](https://github.com/conway220/anova_wifi/commit/ce956a217cf665f93e791701de83e14211bb44d2))
