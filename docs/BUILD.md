<!-- coderabbit-ai-generated:v1 -->

<!-- coderabbit-ai-generated-section:v1:a8e6b8e331b19c14d11bb4130cb85d1845bab0f143d95a277fb013bd339cee93 -->

<!-- coderabbit-ai-generated-section:v1:c8ec148903cbd160e2c1b078b2d8cf68ed4866369e42ce6826f07fda5d4b1eb2 -->

<!-- coderabbit-ai-generated-section:v1:72e9c7f1c1216ba5dcb62b32b4d09179add2c5b72e70cb1983440cf7678bc9f8 -->

<!-- coderabbit-ai-generated-section:v1:9ecd51a28a35256cf798f0abe6672a694e2d4a3c14c3684fc1140fe3e53c4ead -->

<!-- coderabbit-ai-generated-section:v1:fe5b85bbfb07a9b67e9550758437006df6b4f96308d34d3ffb470da0f1c6070b -->

# Build & setup guide

[← Project overview](../README.md)

Adds an opt-in **BOTW EU: preload all recorded pipelines before play** checkbox to the Xbox/Windows host launcher and `<BotwFullPreload>true</BotwFullPreload>` under `<Graphic>` in `settings.xml`.

Target: `00050000101c9400` only. Patch base: Cemu-UWP **d3d12-backend**, commit [`522d3498b5a8b3854d01909950c3738de5c94aa2`](https://github.com/PrismFox67/Cemu-UWP/tree/522d3498b5a8b3854d01909950c3738de5c94aa2). The linked repository's `main` branch lacks the UWP/D3D12 implementation at inspection time. This repository contains a portable patch because the connected `idfk` repository was empty.

## Separate Xbox installation

Apply **both** patches below to build **Cemu BOTW Precache**, an independent app intended to coexist with PrismFox67's build.

| Setting | Custom value |
|---|---|
| Package identity name | `Coolkool2233Pixel.CemuBOTWPrecache` |
| Publisher / signing certificate subject | `CN=Coolkool2233Pixel.CemuBOTWPrecache` |
| Xbox tile and package display name | `Cemu BOTW Precache` |
| Publisher display name | `coolkool2233-pixel` |
| Application ID | `BotwPrecache` |
| Launch protocol | `cemu-botw-precache:?path=<encoded-game-path>` |
| Phone product GUID | `6aa7e43b-2294-5476-882f-fd936a38f5d1` |
| Local build directory | `build-botw-precache-local` |
| Local signing key | `build-botw-precache-local/CemuBOTWPrecache_local.pfx` |
| CI download archive | `cemu-botw-precache-uwp-x64.zip` |

Windows derives the package full name from the identity fields. Its shape for the default local build is `Coolkool2233Pixel.CemuBOTWPrecache_0.1.900.0_x64__<PublisherId>`; the actual publisher suffix is generated during packaging. The package family changes because both the identity name and publisher differ. [Microsoft's package identity documentation](https://learn.microsoft.com/en-us/windows/apps/desktop/modernize/package-identity-overview) explains these names and how app data is scoped to a package family.

The second patch updates the manifest, local and CI signing settings, launcher About heading, protocol registration and current CI archive name. It also stops checking PrismFox's releases for app updates: install future custom builds manually. Existing upstream credits are retained. The local build script restores the original manifest bytes after version stamping, preserving the customized identity even before you commit the patch.

Follow the [step-by-step Xbox installation guide](INSTALL-XBOX.md) to install the MSIX through Xbox Device Portal as **Cemu BOTW Precache** while leaving the existing app installed. The generated MSIX filename may still start with `CemuBin`; Xbox uses the manifest identity for installation. **Actual simultaneous installation still needs verification on an Xbox.**

This identity creates separate app storage and settings. Existing saves, keys, installed updates/DLC and caches remain with the original package until you copy them to the custom package. To keep external storage independent too, choose separate external save/data folders for the two apps; explicitly selecting the same USB folders shares those files. Update any external frontend launch links to the new protocol.

Keep this identity and signing key for subsequent custom builds, and increment the version (for example `& .\tools\build-uwp-local.ps1 -Version "0.1.901.0"`). The second patch changes the app identity intentionally; it does not migrate or delete the original app's data.

## What is possible

The fork already compiles transferable shaders at startup and can rebuild recorded D3D12 pipelines on its loading screen. Its Quick start option defers most pipelines until gameplay, and its preload selector excludes pipelines unused for 20 sessions. See the original [loader](https://github.com/PrismFox67/Cemu-UWP/blob/522d3498b5a8b3854d01909950c3738de5c94aa2/src/Cafe/HW/Latte/Core/LatteShaderCache.cpp) and [pipeline implementation](https://github.com/PrismFox67/Cemu-UWP/blob/522d3498b5a8b3854d01909950c3738de5c94aa2/src/Cafe/HW/Latte/Renderer/D3D12/D3D12PipelineCache.cpp).

This patch changes that selection for the requested title when opted in:

- Enable the pipeline loading phase even if the general pipeline option is off.
- Override Quick start for this title and wait on the existing loading screen until the recorded work finishes (or existing stop handling cancels loading).
- Include old entries excluded by the 20-session filter.
- Keep the existing worker limits, shader validation, crash quarantine and cache formats. Defaults and other title IDs keep their previous behavior.

**This compiles known cache entries; it cannot enumerate unseen shaders or pipeline states from a title ID.** A first launch with empty caches has no recorded work to preload. Unseen effects, missing shader dependencies, compiler failures, changed graphic packs and pipelines evicted under memory pressure can still require compilation or produce missing effects. The existing progress counters count attempted/submitted work and are not proof that every driver compile succeeded.

UWP uses Direct3D 12. A Vulkan `_vkpipeline.bin` cache is not a D3D12 pipeline database. The fork documents that the Xbox driver cannot persist its pipeline library, so pipelines may need rebuilding on each launch even after bytecode is cached. Compilation needs the target renderer/device initialized: building an MSIX cannot bake Xbox driver pipelines offline. See the original [D3D12 cache notes](https://github.com/PrismFox67/Cemu-UWP/blob/522d3498b5a8b3854d01909950c3738de5c94aa2/src/Cafe/HW/Latte/Renderer/D3D12/README.md).

## Existing configuration you can try without rebuilding

In a compatible upstream build, enable **Compile pipelines while the game loads** and turn **Quick start** off. Keep **Compile shaders asynchronously** enabled, with **DXC** selected. Those existing settings already move eligible recorded work to startup. The patch adds title-specific forcing and includes the old entries.

Equivalent values inside the existing `<Graphic>` element (edit while Cemu is fully closed; preserve the rest of the XML):

```xml
<PrecompilePipelines>true</PrecompilePipelines>
<PrecompileInBackground>false</PrecompileInBackground>
<PrecompileInBackgroundDefaultOn>true</PrecompileInBackgroundDefaultOn>
```

The migration marker is needed on the pinned version: without it, configuration loading turns Quick start back on once. The launcher saves the marker itself when saving settings.

## Build in GitHub Actions

The **[Build Xbox MSIX workflow](https://github.com/coolkool2233-pixel/idfk/actions/workflows/build-xbox.yml)** compiles the pinned upstream source with both patches on a Windows 2022 runner. **[Build 44286445115 passed](https://github.com/coolkool2233-pixel/idfk/actions/runs/44286445115)** on 18 November 2026 and produced the signed x64 package `0.1.902.0` from project commit `f420abf8aa181f58942220e9e328ab38a681ed1d`.

**[Download the verified Windows build artifact](https://github.com/coolkool2233-pixel/idfk/actions/runs/44286445115/artifacts/14421890902)** (about 68 MB; GitHub sign-in required). Extract the downloaded Actions ZIP, then extract `cemu-botw-precache-uwp-x64.zip` inside it. The app package is `CemuBin_0.1.902.0_x64.msix`; its manifest gives it the custom Cemu BOTW Precache identity. The artifact expires **2 December 2026**. Save a copy or run the workflow again for a new build.

1. Open the workflow in the repository's **Actions** tab. The first workflow push starts a build on the task branch. For another attempt, select **Run workflow** and choose the branch containing the patches.
2. Wait for **Cemu BOTW Precache · x64 UWP** to succeed. A cold dependency build can take an hour or more.
3. In that run's **Artifacts** section, download `cemu-botw-precache-uwp-x64`. Extract the Actions artifact, then extract the package ZIP inside it.
4. Install the MSIX through Xbox Device Portal, using any included x64 dependencies required by your device. The download includes the public test signing certificate and `build-info.json` identifying the project commit, upstream commit and package version. Private signing material is excluded.

The workflow verifies the generated package's custom name, publisher, x64 architecture and presence of a signature entry before uploading. A successful build still needs an Xbox installation/gameplay test. If the workflow fails, open its failing step or download `xbox-build-logs` from the run. Private-repository Actions access and runner availability depend on your GitHub account/repository settings.

The workflow version starts at `0.1.901.0` and increments with its run number. Builds use a temporary self-signed test certificate; this workflow does not publish a release or deploy to a console.

## Apply and build the patch

Extract this package and open PowerShell in its root. Use a clean checkout for patching. The commands pin the exact tested base; newer source revisions may need manual porting.

```powershell
$patch = (Resolve-Path .\patches\0001-botw-full-preload.patch).Path
$identityPatch = (Resolve-Path .\patches\0002-independent-xbox-package.patch).Path
git clone --branch d3d12-backend https://github.com/PrismFox67/Cemu-UWP.git ..\Cemu-UWP
Set-Location ..\Cemu-UWP
git checkout 522d3498b5a8b3854d01909950c3738de5c94aa2
git apply --check $patch
git apply $patch
git apply --check $identityPatch
git apply $identityPatch
& .\tools\build-uwp-local.ps1
```

Stop if a patch command reports an error. If you already applied `0001`, apply only `0002` before rebuilding. Run the build on Windows with the prerequisites expected by the fork's [local build script](https://github.com/PrismFox67/Cemu-UWP/blob/522d3498b5a8b3854d01909950c3738de5c94aa2/tools/build-uwp-local.ps1): Visual Studio 18/2026 Community C++ tools and Windows/UWP SDKs, Git/OpenSSL, and CMake 4.2+ available as appropriate. The script has a hard-coded Visual Studio installation path: inspect it for your machine. It initializes submodules/vcpkg as needed; the initial dependency build can take an hour or more.

The script writes the signed package under `build-botw-precache-local\AppPackages`. Install it through Xbox Device Portal following the fork's [tester guide](https://github.com/PrismFox67/Cemu-UWP/blob/522d3498b5a8b3854d01909950c3738de5c94aa2/docs/XBOX_TESTERS.md). Back up saves before changing installed packages.

## Supply the cache input

Close both emulator instances before copying. Collect these two files using your game and the same fork's **Windows D3D12 renderer**, then copy them together into the target's active `shaderCache/transferable` directory:

```text
00050000101c9400_shaders.bin
00050000101c9400_d3d12pipelines.bin
```

Use the same game revision, graphic packs/presets and compatible emulator version when collecting. Explore the areas/effects you want prepared; the database only contains observed combinations. You can also reuse caches already collected on the Xbox itself. No game data or cache database is bundled here.

On the default UWP layout, the destination is the **Cemu BOTW Precache** package's `LocalState/shaderCache/transferable` via Device Portal. If Settings → Folders selects an external Cemu data folder, use that folder's `shaderCache/transferable` instead; check the log for the actual active data folder. Settings and logs remain in the app's own storage. Transfer the shader cache and D3D12 recipe file, preserving their exact names; do not rename Vulkan recipes or copy a PC driver cache as an Xbox substitute. Existing caches are not merged by this patch: back up the target files before replacing them.

## Enable and verify

1. In the patched launcher Settings, enable **BOTW EU: preload all recorded pipelines before play**. The UI warns about longer loading and greater memory use. Alternatively, set `<BotwFullPreload>true</BotwFullPreload>` inside the existing `<Graphic>` element while Cemu is closed.
2. Launch title `00050000101c9400`. Look for `D3D12: BOTW full preload: preparing all recorded pipelines before gameplay (including old entries)` in `log.txt`, followed by the existing pipeline summary. A zero count means no recipes were available; skipped entries need matching shaders or valid records.
3. Let startup finish. Replay the same route/effects and compare shader/pipeline notifications and frame times with the option off, using identical settings. Test both the first launch with transferred files and a second launch.
4. Check memory use and stability on the actual Xbox, particularly Series S. Loading every recorded BOTW pipeline uses more memory and can exceed the app budget; retained pipelines can also be evicted later. This option trades startup time and RAM for fewer gameplay compiles and does not guarantee a stutter-free game.

Turning the checkbox off (or setting `BotwFullPreload` false) restores the general settings without modifying cache formats or deleting files. To remove both source patches, first reverse `0002` with `git apply --reverse --check $identityPatch` and `git apply --reverse $identityPatch`, then reverse `0001` the same way using `$patch`. Reversing the identity patch returns the original package identity; rebuilding that source produces a package in the original app family.

## Validation included here

With Python 3, Git, OpenSSL and a C++17 compiler, from this package's root:

```sh
python3 tests/check_patch.py /path/to/Cemu-UWP
```

The source clone must contain the pinned commit. The check reads committed files into a temporary directory and leaves your checkout untouched, applies both patches, checks the manifest and local/CI signing consistency, creates a temporary test certificate with OpenSSL, then compiles the patched policy header and actual `BeginPreload` function with fake record storage. It covers 48 setting/title combinations, absent/empty caches, the 20-session boundary, usage ordering, opt-out restoration and the existing 400-entry Quick start fallback. Both patches are then reversed and the original manifest bytes are checked. The manifest restoration guard in the local PowerShell script is checked as source; that local script has not been executed on Windows. The separate Windows Actions workflow successfully compiled, signed and checked the generated MSIX.

These checks passed on Linux with Python 3.14.4, Git 2.53.0, g++ 15.2.0 and OpenSSL 3.5.5. **The [Windows/UWP Release build and package checks passed](https://github.com/coolkool2233-pixel/idfk/actions/runs/44286445115)** in 31 minutes 56 seconds using CMake 3.29 and Visual Studio 2022. The first attempt failed because Windows changed patch file line endings; preserving LF in `.gitattributes` fixed that before the successful build. **Xbox installation, launcher interaction, certificate trust, coexistence and BOTW runtime/performance remain unverified.** The selection checks exercise no GPU or game assets; they do not validate native driver compilation or cache compatibility on a device.


<!-- /coderabbit-ai-generated:v1 -->