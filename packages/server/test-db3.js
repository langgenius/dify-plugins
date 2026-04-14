const request = require("supertest");
const app = require("./dist/index").default;
const { pool, initDb } = require("./dist/db");

async function run() {
  await initDb();
  const companyId = "test-company-" + Date.now();
  console.log("Onboarding:", companyId);
  
  const res1 = await request(app)
      .post("/v1/paperclip/onboard")
      .send({ companyId, agentCount: 2 });
  
  console.log("Res1 status:", res1.status);
  
  const res2 = await request(app)
      .post("/v1/paperclip/onboard")
      .send({ companyId });
      
  console.log("Res2 status:", res2.status, "body:", res2.body);

  const check = await pool.query("SELECT * FROM paperclip_companies WHERE paperclip_company_id = $1", [companyId]);
  console.log("Check DB:", check.rows);
}

run().catch(console.error);
