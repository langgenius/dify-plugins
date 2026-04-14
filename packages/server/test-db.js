const { pool, initDb } = require("./dist/db");
async function run() {
  await initDb();
  await pool.query("INSERT INTO paperclip_companies (id, tenant_id, paperclip_company_id) VALUES ('abc', 'pc_test', 'test-company-1')");
  console.log("Inserted");
  const res = await pool.query("SELECT * FROM paperclip_companies");
  console.log("Selected:", res.rows);
}
run().catch(console.error);
