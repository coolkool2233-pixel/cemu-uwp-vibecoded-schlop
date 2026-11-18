<!-- coderabbit-ai-generated:v1 -->

<!-- coderabbit-ai-generated-section:v1:fb41ed81c9efecb7cc330d264e3b8b935ca608ca3603f63015d15fbbb99ea5ba -->

# Install Cemu BOTW Precache on Xbox

This guide installs the **x64 UWP test build** on an Xbox in Dev Mode using a computer and Xbox Device Portal. The Windows build succeeded, but **installation, certificate trust, coexistence with PrismFox's build, and gameplay have not yet been tested on an Xbox**. Menu wording can vary between console versions.

## What you need

- An Xbox with Developer Mode activated and a user signed in, plus a computer with a browser on the same local network.
- Access to this private repository and its GitHub Actions artifacts. The [build artifact](https://github.com/coolkool2233-pixel/idfk/actions/runs/44286445115/artifacts/14421890902) expires **2 December 2026**; save a copy before then. A later successful build may have a different version and file name.
- Your own BOTW game files. This download does not include games, keys, saves, updates, DLC, or shader caches.
- Optional: a USB drive formatted as **NTFS or exFAT** on a PC, with your game files on it. On the Xbox, select **Use for media** if prompted. The upstream guide notes that an Xbox game storage format is not readable by UWP apps.

## 1. Download and extract the package

1. On your computer, sign in to GitHub and open the [build artifact](https://github.com/coolkool2233-pixel/idfk/actions/runs/44286445115/artifacts/14421890902). If the direct link does not open, visit the [successful build run](https://github.com/coolkool2233-pixel/idfk/actions/runs/44286445115), scroll to **Artifacts**, and choose **cemu-botw-precache-uwp-x64**. Your account needs access to the repository.
2. Save the download and extract the outer GitHub Actions ZIP. Extract the `cemu-botw-precache-uwp-x64.zip` file inside it as well.
3. Find **`CemuBin_0.1.902.0_x64.msix`**. The `CemuBin` filename is expected; the package identity inside it is `Coolkool2233Pixel.CemuBOTWPrecache` and the intended tile name is **Cemu BOTW Precache**.
4. Keep the extracted files together. The package folder may contain `Dependencies/x64` with Microsoft VCLibs, a public `CemuBOTWPrecache.cer` signing certificate, and `build-info.json`. The workflow copies the package output and adds the certificate and build information; the archive contents have not been independently inspected. If a file is missing, check the [build run](https://github.com/coolkool2233-pixel/idfk/actions/runs/44286445115) and report what you see.

## 2. Enter Xbox Developer Mode

1. If Dev Mode is not activated, follow [Microsoft's Xbox Developer Mode activation guide](https://learn.microsoft.com/en-us/windows/uwp/xbox-apps/devkit-activation). It describes installing the Xbox Dev Mode app and registering the console with a Partner Center app developer account.
2. Open **Xbox Dev Mode**, select **Switch and restart**, and wait for the console to enter Developer Mode. Open **Dev Home** if it does not appear automatically.
3. Sign in a user on the Xbox. Keep the console powered on and connected to the same local network as your computer. Retail games and apps are available after switching back to Retail Mode.

## 3. Connect to Xbox Device Portal

1. In **Dev Home → Home → Remote Access**, select **Remote Access Settings**.
2. Enable **Xbox Device Portal**. Under **Authentication**, choose **Set username and password**, set credentials, and save them.
3. Return to the Dev Home **Home** tab. Note the full URL shown under **Remote Access**, including its port and `https://` prefix if shown.
4. On your computer, enter that exact URL in the browser. If the browser warns about the portal's certificate, confirm the address matches the one shown on your own Xbox before choosing the browser's option to continue. Sign in with the Device Portal credentials you just set.

The portal's HTTPS certificate warning is separate from the certificate used to sign the app. See [Microsoft's Device Portal setup](https://learn.microsoft.com/en-us/windows/uwp/xbox-apps/device-portal-xbox) for the console menus and connection details.

## 4. Install the app and its dependencies

1. In Device Portal, open **Home** and find **My games & apps**. Choose **Add** to open the installation form.
2. Browse to the extracted **`CemuBin_0.1.902.0_x64.msix`** and select it as the application package.
3. In the dependency section, add the **Microsoft.VCLibs** package from the extracted **`Dependencies/x64`** folder if present, following the [upstream Xbox tester guide](https://github.com/PrismFox67/Cemu-UWP/blob/522d3498b5a8b3854d01909950c3738de5c94aa2/docs/XBOX_TESTERS.md). Add any other x64 dependency the installer specifically requests from that folder. Do not select the main MSIX as a dependency.
4. Submit the form and wait for Device Portal to report that installation has finished. Look for **Cemu BOTW Precache** in **My games & apps** and in Dev Home.
5. If the portal reports a signing or certificate error, keep the error text and the included `CemuBOTWPrecache.cer`. This build uses a temporary self-signed test certificate; trust on Xbox has not been verified. Do not assume importing the certificate on your computer changes trust on the Xbox. Share the exact error before retrying certificate steps.

The package was given its own name, publisher, and protocol to support a separate installation alongside PrismFox's build. **Coexistence is not yet verified on hardware**. Back up any saves before installing or removing packages; the new package has its own app storage and settings.

## 5. Set the app type and launch

1. In **Dev Home**, highlight **Cemu BOTW Precache**, press the controller's **View** button, and choose **View details**.
2. Set **App type** to **Game**. The upstream guide says this gives the app more memory and display options; leave the other dropdown on Retail if shown.
3. Launch **Cemu BOTW Precache** from Dev Home. If it does not appear or fails to start, record the exact Device Portal message or any on-screen error.

## 6. Add your game and enable BOTW preload

1. In Cemu's launcher, use **LB/RB** to open **Settings → Game folders** and add the folder or USB drive containing your game. Refresh the game list if necessary. The launcher shows the game's region and title ID.
2. If your disc image needs a key, use your own `keys.txt` and choose **Settings → Import keys.txt from game folders**, as described in the [upstream tester guide](https://github.com/PrismFox67/Cemu-UWP/blob/522d3498b5a8b3854d01909950c3738de5c94aa2/docs/XBOX_TESTERS.md). Add your own updates and DLC using that guide.
3. In **Settings**, enable **BOTW EU: preload all recorded pipelines before play (longer loading, more memory)**. It applies to title ID **`00050000101c9400`** only. Other BOTW regions are not covered by this option.
4. If you have matching caches recorded with this fork's D3D12 renderer or from an existing Xbox installation, close Cemu and copy both files to the new app's active `shaderCache/transferable` folder:

   ```text
   00050000101c9400_shaders.bin
   00050000101c9400_d3d12pipelines.bin
   ```

   With the default data location, use Device Portal **File explorer → LocalAppData → Cemu BOTW Precache package → LocalState → shaderCache → transferable**, creating missing folders if the portal permits it. If you selected an external Cemu data folder, use its `shaderCache/transferable` instead. Back up existing files before replacing them; see [cache preparation](BUILD.md#supply-the-cache-input).
5. Start BOTW and wait for loading to finish. The first launch with empty caches has nothing recorded to preload, and new effects can still compile during play. The option can increase loading time and memory use; Xbox performance and stability remain untested.

## Troubleshooting

- **Artifact missing or inaccessible:** confirm GitHub access and the expiry date. For a fresh package, see [Build in GitHub Actions](BUILD.md#build-in-github-actions).
- **Portal will not connect:** confirm both devices are on the same local network, the console is in Dev Mode, Device Portal is enabled, and the full URL and port match Dev Home.
- **Install reports a missing framework:** select the matching package from `Dependencies/x64` as a dependency and retry; record the exact error if it is absent.
- **Installation or launch fails:** save the Device Portal error and package version. If the app started, retrieve `log.txt` from the custom package's **LocalState** using Device Portal **File explorer**; after a crash and restart the preceding session may be in `log_previous.txt`. Logs can contain local paths, so inspect them before sharing.
- **Game or preload is missing:** verify the configured game folder, the displayed title ID, and the two cache names. The app does not manufacture a full cache from the title ID.

For more details about cache input, data storage, and verification, see the [build and setup guide](BUILD.md). To return to Retail Mode, use **Dev Home → Quick Actions → Leave Dev Mode** as described by Microsoft; avoid deactivating Dev Mode when you only intend to switch modes.


<!-- /coderabbit-ai-generated:v1 -->