// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { suprawall, FirebaseAdapter } from "@suprawall/core";
import { db } from "./firebase";

// Register the browser-safe Firebase adapter
suprawall.registerAdapter("firebase", FirebaseAdapter);

// Configure SupraWall Core to use the Firebase abstraction
suprawall.config({
    adapter: "firebase"
});

// Since we are already initializing firebase in lib/firebase.ts for Auth and other parts,
// we just pass the db object down into the adapter to reuse it!
if (typeof window !== "undefined") {
    if (!(db as any)._isMock) {
        suprawall.__interop_setAdapterDb(db);
    } else {
        console.error("SupraWall: Cannot set adapter DB because Firebase is not initialized correctly.");
    }
}

export { suprawall };
