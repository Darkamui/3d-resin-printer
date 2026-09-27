# Production log

Historical notes from asset production. The public repository includes the final assets and validation reports. Intermediate checkpoints, milestone renders, supplied reference photos, and production briefs are archived separately; the build scripts regenerate checkpoints and milestone previews locally.

## Preparation

- Read the complete handoff, dimensions note, and all three supplied photos.
- Confirmed Blender 5.2.1 LTS is installed. Live Blender connector is unavailable; isolated background processes will produce assets without changing an interactive scene.
- Resolved reference conflict in favor of the original brand-neutral design requested by the handoff.
- Reviewed the official product reference: https://www.elegoo.com/products/saturn-4-ultra-16k-10inch-monochrome-lcd-resin-3d-printer . Reference features are inspiration, not a claim of exact reconstruction.

## Milestone 1 — reviewed

- Saved `checkpoints/m01.blend` and inspected `renders/milestones/01_blockout.png`.
- Footprint, lid seating, base proportions and framing are coherent. Molded hood is a closed 3 mm shell with an open bottom, locating lip and gasket.
- Cover is too cloudy at current settings; adjust transmission/roughness in milestone 6. Hardware is visible faintly but needs the intended transparent material pass.
- User confirmed continuing with the original design after briefly considering a close Saturn reconstruction.
- Actual overall height includes the handle: 682.5 mm; shell roof is 665 mm. This remains within the handoff range.

## Milestone 2 — reviewed

- Inspected the cover-off mechanical render. Twin rails, central helical screw, bearing supports, clamp lever and plate carrier read clearly.
- Added a real open vat, distinct 0.15 mm film, lower clamping rings, perimeter bolts, locking knobs and a cut pour notch.
- The upper bearing and carriage bridge connect visibly. The plate has leveling guide pins and a captured joint rather than a single supporting rod.
- Corrected material persistence between background Blender runs by retaining the material library explicitly.

## Milestone 3 — reviewed

- Inspected the exposure render at 1200 px. The 84-package LED matrix, individual collimators, reflective chamber, spreader and separate LCD layers are visible.
- The LCD supports are annular, leaving an unobstructed exposure aperture. Film-to-protector clearance is 0.275 mm in the visualization pose.
- Per-layer explosion offsets are provisional and will be arranged explicitly in milestone 7 to avoid confusing layer order in the final review images.

## Milestone 4 — reviewed

- Inspected the housing-off render. Frame and gussets support the deck independently of the outer panels; wiring routes occupy the side and rear corridors.
- Review exposed insufficient board support under several standoffs. Added dedicated trays, pillars and hanging brackets in milestone 5, including PSU isolation mounts.
- PSU, mainboard, LCD board, USB board, distribution board and three modeled fans are present. Fan blades are solid geometry.

## Milestone 5 — reviewed

- Inspected the detailed front three-quarter view. Panels have real thickness, open intake/exhaust slots, folded return flanges, screws and panel gaps. Portrait touchscreen and USB hardware fit their openings.
- The lattice sample initially had support endpoints offset from the lattice nodes. Corrected all three states during milestone 6 so every support touches the raft and an actual lattice node.
- Generic markings replace brand graphics. Sample state collections are mutually exclusive; the complete state is visible by default.

## Milestone 6 — reviewed

- Reviewed front and rear material renders. Full transmission and a lighter amber tint reveal the mechanism while retaining a tinted enclosure.
- Added UV maps to the enclosure, panels, boards, glass and plate. Materials use portable Principled PBR inputs; no lighting is baked into textures.
- Added very fine geometric machining marks on the build plate underside.

## Milestone 7 — reviewed and corrected

- Master contains separate assemblies, sensible functional origins, unit scales, and an independent capped cutaway of the front-right housing, vat, LCD and optics.
- The first exploded render put the plate inside the lifted cover. Increased cover clearance, lowered the exploded plate, and reframed the camera. The reviewed correction separates those parts visibly.
- Rear review exposed a USB cable overshooting its control points through the side panel. Restricted its Bezier handles to the internal cable corridor; the corrected rear render has a clean side panel.
- Extended the vat locking shafts to engage their threaded inserts and recessed the IEC pins into a modeled inlet mouth.
- Signed-volume checks found 21 fan blades with inward face winding. Corrected source and cutaway blades before export.
- Editable Blender curves and text produce coincident cap seams when evaluated. The audit welds these at 1e-8 m, matching export preparation. All resulting production surfaces are closed; the master retains editable curves and text.

## Milestone 8 — complete

- Exported the assembled and explodable GLBs and six subsystem GLBs. The explodable file contains one coordinated `EXPLODED_VALIDATION` clip.
- The first exporter run split animations by object. Disabled that Blender exporter option, then verified the entire assembled and exploded hierarchy after import into empty scenes.
- Compared triangulated surface area and signed volume, rather than comparing nonplanar n-gon measures against triangulated GLB measures. Ignored unused material slots; checked every material actually assigned to faces.
- Removed submicron triangulation slivers around hex sockets and panel bevels in disposable export geometry. This fixed all re-imported corner-normal warnings while retaining editable source topology.
- Rebuilt smaller controller boards with component counts and orientation appropriate to their substrate dimensions. Fixed a parent-transform evaluation issue exposed by the electronics close-up and reviewed the corrected result.
- Final Blender master: **1,642 production nodes, 939,832 evaluated triangles**. Final GLBs: **934,388 triangles** after export cleanup.
- Both primary GLBs pass: no missing nodes, hierarchy mismatches, geometry changes beyond float precision, material loss, open geometry after welding, nonfinite normals or nonunit normals. Maximum bounding-box difference is **1.49e-8 m**. Maximum exploded transform matrix difference is **2.38e-7**.
- Rendered all eleven required views plus cutaway, side and top, at **2000 × 2000**. Corrected LCD layer review transforms and reframed the UV housing to fit the image.
- Replaced the flat studio horizon with a seamless curved backdrop for straight-on views.
- Saved `reports/geometry_audit.json`, `assembly_manifest.json`, `export_expected.json`, `export_mesh_cleanup.json`, `roundtrip_validation.json`, and `delivery_manifest.json` as review evidence.
- Inspected a fresh Cycles render of the re-imported complete GLB (`renders/milestones/08_glb_roundtrip_hero.png`); the enclosure, materials and mechanical geometry remain visually intact.
- File completeness and checksum check passes for all 23 primary delivery files. `checkpoints/m08.blend` is a copy of the delivered master.
