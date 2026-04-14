const { pool, initDb } = require("./dist/db");
async function run() {
  await initDb();
  await pool.query("INSERT INTO paperclip_tokens (id, token, tenant_id, paperclip_company_id, tier, expires_at) VALUES ('123', 'tok123', 'pc_test', 'testco', 'dev', '2027-01-01 00:00:00')");
  console.log("Inserted");
  const res = await pool.query("SELECT * FROM paperclip_tokens WHERE token = $1", ["tok123"]);
  console.log("Selected:", res.rows);
}
run().catch(console.error);
