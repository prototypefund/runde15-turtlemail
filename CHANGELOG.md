# Changelog

All notable changes to this project will be documented in this file.

## [0.7.1] - 2024-07-25

[a1bc504](a1bc5046281352032c693b9e89faba07fd135c7a)...[5c358c8](5c358c872e25770e30b75901425ec35378b41ff7)

### Bug Fixes

- Add missing translations ([a8926c6](a8926c696a9482ab81e98a17553303b8c5f703f6))
- Line endings ([27afd70](27afd70190c1f45d8b74590496aee4a1a95d6cdb))
- Redis channels serialization errors ([691ce21](691ce2188bf3c2e990e7061af5e467b1b5c5ad4f))
- Live message status updates ([7cf0689](7cf06892086ca77beaf1b51e3b1c0b6c4b163afa))

### Features

- Add new illustrations ([b288767](b288767af4c635fa78c890d862e8eb7db96b624b))

### WIP

- Fix serialization errors in django-channels ([10842b9](10842b96f5e02228a3375dbd273f3fb4ceb543da))

### Bump

- Release v0.7.1 ([5c358c8](5c358c872e25770e30b75901425ec35378b41ff7))

## [0.7.0] - 2024-07-16

[8316d04](8316d0413c2e9510a218a63a32d52a8337747dfa)...[a1bc504](a1bc5046281352032c693b9e89faba07fd135c7a)

### #50

- Merge main ([7a3df11](7a3df11c232ae94e944d332b5a3f8aad2e9687d7))
- Small fixes, reached first draft review state ([dc9ac5b](dc9ac5bcce1b1b06bf70a1ad8f8080fa111bdb52))
- Review fixes, internationalization of system messages ([87dd6d9](87dd6d91947e43f99b6f7316f86e62c6fc42928e))
- Linting, rebase on main ([5dacb27](5dacb27dadc39c84c366d4e41d3ff4f1bbd8a34f))
- Reformat jinja ([07729e6](07729e617aef9bee70f49be90995eb1738d54235))
- Other linting foo ([9e436da](9e436dab531d71402a9184aa1ad354d9272dc6d4))
- Other linting foo ([372b2ec](372b2ec1651cb28272b8d742893ab31c279900ce))
- Other linting foo ([5233d9e](5233d9e7072ef8d220606a510cd065d756e43213))

### Bug Fixes

- Recompile messages after updating them ([bc1fce9](bc1fce9d862e95d175881b282894d06004b32c0c))
- Remove duplicate translation ([44271b8](44271b86020a82e66fb39e595409838507052cc8))
- Add missing translations ([c159bb4](c159bb45957f421f07c387a844a84266984d2139))
- Template lints ([14806a5](14806a5c4ade81a6951460e6f9a8ebc7dc279a7d))
- Chat menu translations ([ac2e7cb](ac2e7cb7bf1298c3f6ccab401f3d88727ea47f28))
- Missing translations ([debbf10](debbf104cb193d7e3c6977e2d324b63f7c26e0e1))
- Only show packet chat link when there is a chat ([2f83332](2f83332b805b6fd6364b9af6dc760dd5cbd1317d))
- Add translations for stay frequencies ([54137c6](54137c6d90f43b59de63330905dfd55f2200433b))
- Add other missing translations ([bea1f78](bea1f781517333a1dc68f6138921bbfce8f4d786))
- Add more missing translations ([97b3ce9](97b3ce98c18e8d9838f5ef02ef13bd8dbdd549d6))
- Add missing channels-redis dependency ([1f09dd9](1f09dd90b7e93f3ab66ae8bc2391605177d8712a))

### Features

- Added German translation of frontpage ([eee31c9](eee31c9e23c5870d1417613d5c7fd6271d413c45))
- Add, update and delete locations ([c86792b](c86792b73da6bacb3c86c7fcf3acdbd85cfdca26))
- Hide signup links on index page ([64bb7db](64bb7dbf6cc9367e4371a10921ec05c7c164849b))
- Allow users to report problems during handover ([5d4dcbc](5d4dcbc5eb83980412adc66d563ee7db38660329))
- Allow users to cancel accepted and ongoing route steps ([6dea237](6dea237179d41cee47387c05b3ab2ab724894b6e))
- Show stay settings in profile ([04f985b](04f985bf0334066df4d05b276cdc8fb1da14e99b))
- Use index page layout for legal & privacy pages ([8b9e3c7](8b9e3c70c183cd57288a6ecd64805837a49405bb))
- Add german screenshots to landing page ([cb63079](cb63079928f178d7b759927d1feb8378e447b97d))
- Setup huey integration ([dcdf0c3](dcdf0c3faa2275c85528e3387f58b44571841996)), Co-authored-by:Konrad Mohrfeldt <km@roko.li>
- Continuously look for missing routes in the background ([5028b67](5028b675cab2044b1aeebb5bf51d79ad2f17214c))
- Link to chat from packet page ([80d930b](80d930b740e80047f4ecdad5aab9385b97a8aa69))
- Make chat UI mobile-friendly ([c11d1d0](c11d1d004ae81d67f0cdd6b0eb46a489e90de21c))
- Remove some of the weird color names for human ids ([4c3896b](4c3896b41464b959e9d5ccaf61f1e7ff761ddfff))
- Add django channel configuration through env vars ([1b67a21](1b67a21da6c3458e3f3e08070b2b74e3c4acdb21))

### Miscellaneous Tasks

- Add format make task ([e3c8490](e3c849027f6757bf10d55107c8ce7278bb5c2035))
- Mount source code in dev worker container ([5cd9e7a](5cd9e7a22b28f21a7b9e0f7e187a29ee38b68df1))
- Remove old & incorrect fixtures ([1a1ebc1](1a1ebc1914493e2c8659740ef060f8bf41492854))

### Bump

- Release v0.7.0 ([a1bc504](a1bc5046281352032c693b9e89faba07fd135c7a))

### Wip

- Design chat layout ([563464c](563464c0d6254685662dcdd01afc8cd1f9fd48ad))
- Improve chat mobile layout ([49288a3](49288a3da2e914ec7ede726535db6c429c34bfff))

## [0.6.1] - 2024-07-04

[2f07b94](2f07b947abeebe414843fbd1853e919045d3a4aa)...[8316d04](8316d0413c2e9510a218a63a32d52a8337747dfa)

### Bug Fixes

- Vite container permissions ([4b940b3](4b940b3ead8ad37e123a37abd0877c34fb61df0e))
- Allow running tag pipelines ([bf84053](bf840536c8dafff929e78e43743d3baf9634b32c))
- Always run manually triggered pipelines ([a510fec](a510fec20bdf70b1a60ca13c649b0073ab5c0404))

### Documentation

- Add instruction for installing poetry dependencies ([a32dd1a](a32dd1afaf78dab3c04484f207a172e59f4e041a))

### Miscellaneous Tasks

- Update changelog ([9c1f28d](9c1f28dddbc09f8d232db66bc2df3516dcacbaf8))

### Bump

- Release v0.6.1 ([8316d04](8316d0413c2e9510a218a63a32d52a8337747dfa))

### Wip

- Rebase main ([64f3a94](64f3a9411cbe096879d14ca50f8d6e8b3094dcb0))
- #50 Packetübergabe Chat: django channels ([b62bfa2](b62bfa299d28433ad0a57afdf5737daeff74f7b9))
- #50 Packetübergabe Chat: chat ugly but working ([e4ebeed](e4ebeed88621006529b95bb4f61300eacf4af0f4))
- #50 Packetübergabe Chat: message receipts ([58ca30c](58ca30c8c9392fbf4f0fd38462abe26942ff08fb))
- #50 Packetübergabe Chat: highlight active chat ([df6e39b](df6e39b8c02c25516a6ed43f3c6bbc7da20e3442))
- #50 Packetübergabe Chat: highlight updated chats ([c51cbad](c51cbad4eb9b5f821f10f8bf21328d91a8af5fbb))

## [0.6.0] - 2024-07-01

[612a6bc](612a6bc389f7375afaf4390a5a77b9de346a2d1b)...[2f07b94](2f07b947abeebe414843fbd1853e919045d3a4aa)

### #43

- Rebase to main ([5d24285](5d24285469c79efe3478a4ffb2d59b4ef99e92b8))

### #50

- WIP Paketübergabe Chat, models, basic stuff ([bc9a454](bc9a4540800ab0235107a9f9d6b703320dd48ba5))

### Bug Fixes

- Format an unformatted migration ([62773d0](62773d073f39a92e00c8ee9a951e6ea94a52fc49))
- Re-order configuration settings ([879f259](879f259f1eb4651e88841c8d51d06f575d9c33b5))
- Ensure TURTLEMAIL_MAX_ROUTE_LENGTH_DAYS is converted to the expected type ([16606e1](16606e197b620af11c010991dfc8901cd335c6d0))
- Prevent users from sending a packet to themself ([f595031](f5950314fc9ffd11e703bc9c79ba2d323c9dd0e0))
- Move static assets into django folder ([f80cf91](f80cf910ced857663c75283b8179970fbabea1e1))
- Only use english-language screenshots for now ([340d111](340d111a094284cd1911b16caa280dae0486f5a4))
- Disable ASGI lifespan protocol ([2049351](204935179c7ce2711d0514e6d77aee4e6c297a56))
- Htmx.ts formatting ([87aa55b](87aa55b3d417c850bf5448c9f087189d0baf72ac))

### Features

- Use animal IDs for new packets ([00cbb24](00cbb2437d4a271202568784d430a82e190655a1))
- Add german translations ([1725b76](1725b76d19f9d27f519f80d226cb5c6a0b81b53b))
- Add new logo and custom color theme ([3c38344](3c38344fcb0ec10862dbfdf4d329788c76f88ead))
- Add landing page ([7c8b7ec](7c8b7ec04958981c79669ff3666e32c27949f849))
- Show a message on unknown errors ([cd2d5bf](cd2d5bf62d6b285e2e86aff0ab44d089b0b9f168))

### Miscellaneous Tasks

- Update instructions for releasing a version ([84eb322](84eb3220cb8ba62c64ab26cc5d06c63e617e57b4))
- Fix request.user type for views requiring login ([407eff3](407eff3f4fc20e8e35bbf5d4a4a794f544b46bef))
- Bump gitlabfilet ([f267534](f267534a3a1b168c6344085a418c8a0a546862db))
- Add deployment to staging and production environments ([7bb4911](7bb491120bcb0fc86bae5c94478fa7499b6ec7fc))
- Add makefile command for generating migrations ([aaf6742](aaf6742ce19461c2583a488bdf2978ae2948a802))
- Configure prettier to match eslint formatting ([5eb510d](5eb510dd5e7e975ce0fdd375fcaae2069ce2eb9a))
- Skip CI for commits starting with "wip:" ([98d06a5](98d06a5287672d98bca5a218ffdf2add92096f51))

### Bump

- Release v0.6.0 ([2f07b94](2f07b947abeebe414843fbd1853e919045d3a4aa))

### Wip

- #50 Packetübergabe Chat ([a6cec75](a6cec759a77ab74ae7fccb1aa8b74c43fa2f0bf0))
- #50 Packetübergabe Chat ([9f0851d](9f0851d3b03ada9450af940e65ce103af4bfc17b))

## [0.5.0] - 2024-06-17

[d65b6fa](d65b6fac5f655663f72b35a5f63986476bd35d8c)...[612a6bc](612a6bc389f7375afaf4390a5a77b9de346a2d1b)

### #43

- Sendungsverfolgung ([3ac30b0](3ac30b0cd299b1fc208d8eea0967c96eb228c42a))
- Linting migration ([aaac360](aaac36020ebc6ed5f435bc0ab9d98fef4083fcdf))
- Mr review ([7500104](7500104855113b37399f62c3352194dce4238c9b))

### Bug Fixes

- Get_overlapping_date_range for non-overlapping ranges ([574f232](574f232d8aa48f8e54e391c561e5a37c204e0148))
- Only allow selecting users own locations for stays ([80322c9](80322c9e62088b22b42792836acc14b67da23607))
- RouteStep.get_overlapping_date_range for non-overlapping ranges ([90b1bdb](90b1bdb81372e4fac263b4a41b0a8ac3d02ee00a))
- Allow going back from create packet form ([eb7c131](eb7c13110abc3d0335bb40f2050543ff2d714c46))
- Only show request handover messages between differing users ([9b843dc](9b843dcd31a3e1a77d81f544be47b5df946abe93))
- Permissions for updating route requests ([583672c](583672cd2ef457c3b2534081860ff1acb11dd185))
- Mark routes with cancelled steps as outdated ([4667a6b](4667a6b762d4fd2be22253e4a0c31a352e0b8e35))
- Create delivery logs when changing stays with active routes ([ec696d9](ec696d9ae7c1addcf5dfeabf046e4c3a23856b8f))
- Exclude deleted stays when looking for starting stay in a route ([bb64f4a](bb64f4aa7a87419a598547666b9417bb0807d056))
- Only select once stays that are not in the past ([d604d26](d604d266b50aa537d226003f2c0f3ee74ccdb898))
- Add icon for route_outdated packet status ([b63bcde](b63bcde6b746c260726985c656817276a55e321a))
- Permissions in vite container ([ccb40ca](ccb40ca2c1b32966328fa910e520b299faeee712))
- Envs for older docker versions, updated readme ([05d6755](05d6755bcd5b37516f49fa8f3594db040c7c0422))

### Features

- Add basic routing algorithm ([6633b51](6633b5128643ac62b60bbe47719e74f131806e80))
- Show delivery logs on packet detail page ([f489682](f4896824482c0bc18b85ebdfa94d7be84586e90a))
- Search for route when creating a packet ([6a70829](6a708297d8b0238c1124e4a2f76857b8c0e6cade))
- Improve route step display on packet detail page ([bd18958](bd18958d1329c16d8129579171ca6de96a42faae))
- Allow accepting or denying suggested route steps ([d4ef389](d4ef38960b94b75ca55939fcc5e3739ab3eedc28))
- Edit route requests on packet detail page ([3e4320c](3e4320c3c718246a70a5ba308661f80262f10711))
- More delivery log details on packet page ([8b49023](8b490232b509dc73aa38d79f482cd1c8a7acf9b4))
- Set inactive_until in stay edit form ([beea750](beea7507a1e710c94cac41b07f751c559997f6a8))
- Start routes with exactly one of the sender's stays ([bbd30b6](bbd30b610f2c74c7c5cb42280e8a1ea87fe9da32))
- Allow deleting stays with only suggested route steps ([de39e4c](de39e4c56e1756a2dee40b00d77dc5905c036804))
- Show route step progress on packet detail page ([43acb41](43acb41af4303e1ddc5bfca635c0b00c7edfe820))
- Improve wording for route request locations ([09f1154](09f11544e9b134b63aedf64c962d943550be0c67))
- Order Route Steps by start date ([f079a47](f079a4721ee74315546839d3dd3849067f1a9196))
- Describe delivery log changes in more detail ([e84d16c](e84d16cbc7848bf087142005bbcaef19e86dcb5b))
- Add cancel button to stay update form ([92f2ead](92f2eadd4a450ac96b409d3bc01ba2eed88ce212))
- Recalculate routes when any of their stays change ([f27adfd](f27adfddfbd0c44547bfe43dc728750b2bc0f1da))
- Make max route length configurable via env var ([1dbce35](1dbce3592e4eb4712fbbfee2d33fc8f45835538d))
- Add cancel button for route step request form ([a52a839](a52a839a8ff8b1b90bd923c469c4ed252e962240))
- Deliveries list ([950ac1e](950ac1e5b97814f32203a196d9a0a96adaa7f6a3))

### Fix

- Routing for multiple once stays from the same user ([d51695b](d51695b6230ece9f0ed52def544e484c9389396e))

### Miscellaneous Tasks

- Add Makefile test task ([5649a3d](5649a3d43f7333023c5e20cdb9e76b85288cf92e))
- Add logger for showing debug logs ([33c2913](33c291303bd74c17c79b383e55812a08c578f2ea))
- Use human_id for referencing packets ([e13ed81](e13ed81e9ff554f787023378250016dfae4012be))
- Add stay model to admin interface ([0711068](0711068e9e4fdb4c44270d595b3b73f26888ced1))
- Add dump-fixtures task for adding new database fixtures ([8f005ab](8f005ab1e06e2febe05ae30b9d4a1b6df32c8c10))
- Run database for tests in CI ([417aa0d](417aa0d29377a985037120800799b899898ba14e))
- Add new fixtures for testing ([7a4efd2](7a4efd2e7b4892eb96392723b63a01e7f2dbcdbb))
- Consistently use RouteStepRequest term ([0cd3db3](0cd3db324513beb1e35368f255b48c12ce8fa17a))
- Improve admin UI for routes and routesteps ([2862cee](2862cee2ebe154b17dd2877c5bac486d18f4611c))
- Remove obsolete TODO ([52cba50](52cba50696bb8570e6c0daa6324ad0245a4b5780))
- Fix some typing errors ([6dda15c](6dda15c7c4288757f11e04c1f8265eaa6298a069))
- Add small missing migration ([7f525a3](7f525a319809be2a975d9c4038b5a81d30af7ea5))

### WIP

- Sendungsverfolgung ([4ca1ee7](4ca1ee7f3bd712c6312dca0ea28d88f1b59f6efb))

### Bump

- Release v0.5.0 ([612a6bc](612a6bc389f7375afaf4390a5a77b9de346a2d1b))

## [0.4.0] - 2024-06-03

[da1ca88](da1ca880473b366ba92adf708f13e2a920dccfb1)...[d65b6fa](d65b6fac5f655663f72b35a5f63986476bd35d8c)

### Bug Fixes

- Do not push all branches when releasing new version ([34f7282](34f7282fbe9d782a4eeeab619028caaa068b1a0f))
- Use nav element for desktop navigation ([1a2068b](1a2068b6c6052fbcb098ad6a58f3375a820ded98))
- Use h1 in login/signup form ([3682da5](3682da56dec2a588fe14e087a8f17dadf722640e))
- Badges on profile showing wrong data ([273e04b](273e04ba164453e3e532bf9fd0d4edaa30116177))
- Only allow some users to view packets ([bb3c830](bb3c830e85f4622c642fed69801ddf5fa92d8ce2))
- Skip lint task in CI test pipeline ([e1970f4](e1970f4b680b364a774269bf660dd691f9cdbf0b))

### Features

- Add packet creation form ([5d53b6f](5d53b6f70cf691c5af61405eb63283cd9e5c2e6c))
- Added human readable id generator with custom dictionary ([6a5410c](6a5410cc7b59526c4085debf6a7be0529e19c48c))
- Show info on packet detail page ([f20593c](f20593cf2a11caf057cc5c6edfc698985e7f710c))
- Stays list and creation form ([0934c80](0934c8001e940576b02f349d56e4b8bca03f3750))
- Edit and delete stays ([e9ec10b](e9ec10b191612bc88d55eabc7ede53758f993ad1))
- Swap django messages into the page with htmx ([7dfda3f](7dfda3f86cb682509712755452b0d743f30fc60b))
- Link to signup from login and vice versa ([52d3cc8](52d3cc85eca0b87d80f1c27120c41d25730545c3))
- Add user invitations ([6603aa5](6603aa5ec2d888da54f10a3fa40b04cd5ec84478))

### Miscellaneous Tasks

- Reload template changes when debugging ([8ff792d](8ff792d5b0c1432cef13c30ee7c5f45fc60f6128))
- Rename packet receiver to recipient ([d013760](d0137600c34267abbfd30cc0ad6b5248d8cfbc9f))
- Change packets verbose name to delivery ([23d7ae3](23d7ae337b9e63a3ad686c42672c48bf2f7ae3d3))
- Add django-types for better IDE support ([aa1727f](aa1727facca9a5d2420883dd2cd1ea65d695baa5))
- Add GeoDjango app and PostGIS database extension ([7422539](74225392edcfae90e6f87c575c1aeba4bbac7b84))
- Allow modifying dependency versions in dev container ([60c3474](60c3474a9871a439e0e7c281abc59c92082a7885))
- Move location model coordinates to geography type ([f2d012a](f2d012a61d324f17f6d1461bfb5b8e2b76fd3ba9))
- Run database for tests in CI ([73722b0](73722b0fc37d12feef01d8d2f047f35cbbbdc491))
- Add pre-commit hook for missing migrations ([e511ad4](e511ad45ff92dcae65f57071a3c253828dc74441))
- Add pre-commit hook for outdated translations ([a0e7075](a0e70754300aa7003911e0ee3ee427754638b540))
- Update translation file ([024a49d](024a49dc8f2f8efcd12e70b7fb75e7a9637adf3c))
- Install psycopg from pip instead of system package manager ([7fb9075](7fb90751a1a8941a13271a6aab2ef083f95c93cc))
- Show git diff for failing lints in CI ([0ee89ea](0ee89ea6c920a8989bed7eb2a992b3580b60fb70))
- Remove location markers from .po files ([30420ff](30420ff48ee183ade62839483c4fbe55dfb56780))
- Change default from email address ([39976bc](39976bc374551ac4d7b30a62fd450787412709c4))
- Move field templates to field directory ([a18465c](a18465cf7c2513bd3fc4e9bcde961a5993fbd874))

### Refactor

- Move stay form js into its own partial ([3172754](31727541f048541accf7484c56d68b54d48183f4))

### Bump

- Release v0.4.0 ([d65b6fa](d65b6fac5f655663f72b35a5f63986476bd35d8c))

## [0.3.0] - 2024-04-22

[8efca92](8efca9261ca66f43290fecf1bfa00ad457fec209)...[da1ca88](da1ca880473b366ba92adf708f13e2a920dccfb1)

### Bug Fixes

- Add relationship between Location and User ([ec0c3fd](ec0c3fd75f5f642bad16297d6df44f252fd225c9))
- Reference constants in stay frequency choices ([de7b34c](de7b34c57ed112be817c8e6edfe4d77be9391f22))
- Url for redirect to login ([0f322ea](0f322ea155f3cb500b25b7d57ca01b8d48e146e6))
- Require login for some views ([090f0c6](090f0c65a294de6c686f26691128fd6f0f621a15))
- Downgrade eslint to satisfy peer dependency requirements ([476511e](476511ed7d3bcc7432b0180f2afb5763d96f306f))

### Documentation

- Howto run manage.py ([cae0776](cae077687f9f58bb977980cd928fc686e73f1c65)), refs #21

### Features

- Show logged in username in navigation ([9775ef6](9775ef6093223c71113d50d30d03b28099a36337))
- Show user info on profile page ([98b7f7e](98b7f7e100e213dbfba37a36402f33ee1582b7c1))
- Add tm-location-selector web component ([8b65f66](8b65f66c692f2949ebd87c46af916552e1b2a8cf)), refs #19

### Miscellaneous Tasks

- Add packet and routing models ([fb504ae](fb504aecbe4f820e59d1487a8fe4d30be09d9813))
- Bump EcmaScript target ([242092b](242092b2c43c985c6500cad868b0cbe5320fb285))

### Styling

- Add eslint configuration ([832e261](832e261288558293bbaa8d0b75b59ff064df06de))

### Build

- Enable vue support ([fa5c8a8](fa5c8a8d958ea07da3b2effff1e280c34f880142))

### Bump

- Release v0.3.0 ([da1ca88](da1ca880473b366ba92adf708f13e2a920dccfb1))

## [0.2.0] - 2024-04-08

[d377a94](d377a94f99e98a1dea1f46fbf6f155a05d9de052)...[8efca92](8efca9261ca66f43290fecf1bfa00ad457fec209)

### Bug Fixes

- Changelog failing to render sometimes ([c13b876](c13b876a1e0b06e565ca8b59d74a394d164456ee))
- Make fixtures command ([e730b1e](e730b1e478caa359c2606e1efaf2c72333f370db))

### Features

- Add layout with navigation ([b718d92](b718d92ba1ba966b53bb9576054b41cc6e24ad89))
- Add user model, signup and login ([ed83a6d](ed83a6d9669eb194025a944dcff4feaa01dd14f6))
- Location and stay model ([468d9e0](468d9e09973ee1618a7707ea6405a9c98347e1b6))

### Miscellaneous Tasks

- Remove commitizen pre-commit hooks ([78b8a08](78b8a08c811b0ef7e6bd107928e44bd1ffb3e298))
- Replace commitizen with 3 shell commands ([43c693f](43c693f0fda8d615d234a09c84a8339e5b1213d0))
- Add formatting for jinja files ([502ec09](502ec09d3d45f264b054cd71d26a3a2a25b4afd3))
- Add note for updating pyproject.toml on release ([e7f3395](e7f3395e2203da849fff8c249a81e73053eaf0f7))
- Add django user admin ([1f3ebe9](1f3ebe91f797a8506da5c71feefe3940742b74d1))
- Fixtures for user, location, stay ([c4a3d72](c4a3d7225a72073778a0f90fb244c0a2b7cc0d5c))
- Add superuser fixture ([2c1a4f8](2c1a4f8a36248771339f911e341b68158e62cc94))

### Refactor

- Function-based views ([9b8e3b7](9b8e3b7fcf7f88c4823f8e71df26b1d25798f53e))

### Bump

- Release v0.2.0 ([8efca92](8efca9261ca66f43290fecf1bfa00ad457fec209))

## [0.1.1] - 2024-03-24

### Bug Fixes

- Wait for database to accept connections before starting backend ([486326c](486326c89c2bbffecd3a717afa24870cd83b6a2a))
- Fix environment variable syntax for database healthcheck ([40a0f28](40a0f28fe358d8d9ea7f4b184164da009420d1e1))
- Make docker-compose.yml work with older versions of docker compose ([34bc674](34bc674a865fddd647816c783b095de72f082e2a))

### Miscellaneous Tasks

- Setup project ([b8e470c](b8e470ca3b25743207f9f42867c515a85c1d6f99))
- Update readme ([2a2297f](2a2297f8185b4f254fa7238f04c333b4b604854a))
- Add .editorconfig ([cc0eb0f](cc0eb0f9717ce4ce9afa1163ab741e9efe738ed5))
- Add jinja files to editorconfig ([10e43e6](10e43e6cac551ee2533e3e816952229d875c2389))
- Add pre-commit dependency with basic config ([792de51](792de5110010ef0e9d7cad5f265be85aa6517707))
- Run ruff in pre-commit hook ([190a7ad](190a7ad937b8575cb7564d5d31e1055451bee0a0))
- Run pre-commit hooks in CI ([9667723](9667723317b842d2b8cd515472bddb3cedc48ce0))
- Update pre-commit-hooks ([42f6bcc](42f6bcc0e26c4920712699fd608b033b8de6133b))
- Add daisyUI with default themes ([ca084a3](ca084a3664e2a06a0952853857eb22476cc2e4a5))
- Add htmx ([1a676f8](1a676f89745f91097afe2e7e56253343c4d9f8c1))
- Add basic translation extraction and display ([c498d88](c498d88a1449752f87bef2529613527e0755c163))
- Add commitizen package and pre-commit hook ([5a253ea](5a253ea4f2a21dddf89e679d1f4a41ad936be57f))
- Include all commit types in changelog ([95ec2d3](95ec2d30c00d49d78ab11a3984d659844ab5eb9c))

### Bump

- Version 0.1.0 → 0.1.1 ([d377a94](d377a94f99e98a1dea1f46fbf6f155a05d9de052))

<!-- generated by git-cliff -->
