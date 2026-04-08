import "server-only";
import admin from 'firebase-admin';

function getFirebaseAdmin(): admin.app.App {
    if (admin.apps.length > 0 && admin.apps[0] !== null) return admin.apps[0] as admin.app.App;

    let privateKey = process.env.FIREBASE_PRIVATE_KEY || '';
    if (privateKey) {
        // Handle escaped newlines and remove surrounding quotes if any
        privateKey = privateKey.replace(/\\n/g, '\n').replace(/^["']|["']$/g, '').trim();
    }

    const projectId = process.env.FIREBASE_PROJECT_ID?.trim();
    const clientEmail = process.env.FIREBASE_CLIENT_EMAIL?.trim();



    if (projectId && clientEmail && privateKey) {
        return admin.initializeApp({
            credential: admin.credential.cert({
                projectId,
                clientEmail,
                privateKey,
            }),
        });
    } else {
        return admin.initializeApp({ projectId });
    }
}

export function getAdminDb() {
    const app = getFirebaseAdmin();
    return app.firestore();
}

export function getAdminAuth() {
    const app = getFirebaseAdmin();
    return app.auth();
}

// Convenience aliases — safe to use inside route handlers (force-dynamic routes)
export const db = {
    collection: (...args: Parameters<ReturnType<typeof admin.firestore>['collection']>) =>
        getAdminDb().collection(...args),
    doc: (...args: Parameters<ReturnType<typeof admin.firestore>['doc']>) =>
        getAdminDb().doc(...args),
    runTransaction: <T>(updateFunction: (transaction: admin.firestore.Transaction) => Promise<T>): Promise<T> =>
        getAdminDb().runTransaction(updateFunction),
    batch: () => getAdminDb().batch(),
};

export { admin };


export interface OrganizationData {
    stripeCustomerId: string;
    stripeSubscriptionId: string;
    stripeSubscriptionItemId: string; // Needed to report usage to Stripe
    status: 'active' | 'past_due' | 'canceled';
    currentPeriodEnd: admin.firestore.Timestamp;
    operationsThisMonth: number; // Increment this on every SDK call
    lastReportedCount: number;   // Last total pushed to Stripe meters
    hasPaymentMethod: boolean;
    userId: string;
}
