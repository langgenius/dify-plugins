// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

use std::env;
use std::error::Error;
use reqwest::header::{AUTHORIZATION, CONTENT_TYPE};
use serde::{Deserialize, Serialize};

#[derive(Serialize)]
struct EvaluateRequest<'a> {
    #[serde(rename = "agentId")]
    agent_id: &'a str,
    #[serde(rename = "toolName")]
    tool_name: &'a str,
    arguments: serde_json::Value,
}

#[derive(Deserialize, Debug)]
pub struct EvaluateResponse {
    pub decision: String,
    pub reason: String,
}

pub struct SupraWallClient {
    api_key: String,
    api_url: String,
    client: reqwest::Client,
}

impl SupraWallClient {
    pub fn new() -> Result<Self, Box<dyn Error>> {
        let api_key = env::var("SUPRAWALL_API_KEY").map_err(|_| "SUPRAWALL_API_KEY is required")?;
        let api_url = env::var("SUPRAWALL_API_URL").unwrap_or_else(|_| "https://www.supra-wall.com/api/v1/evaluate".to_string());
        
        Ok(SupraWallClient {
            api_key,
            api_url,
            client: reqwest::Client::new(),
        })
    }

    pub async fn evaluate(&self, agent_id: &str, tool_name: &str, arguments: serde_json::Value) -> Result<EvaluateResponse, Box<dyn Error>> {
        if self.api_key.starts_with("sw_test_") {
            return Ok(EvaluateResponse {
                decision: "ALLOW".to_string(),
                reason: "Test mode bypass".to_string(),
            });
        }

        let payload = EvaluateRequest {
            agent_id,
            tool_name,
            arguments,
        };

        let response = self.client.post(&self.api_url)
            .header(CONTENT_TYPE, "application/json")
            .header(AUTHORIZATION, format!("Bearer {}", self.api_key))
            .json(&payload)
            .send()
            .await?;

        if !response.status().is_success() {
            return Err("SupraWall Network Error: Failing closed.".into());
        }

        let resp_data: EvaluateResponse = response.json().await?;

        if resp_data.decision == "DENY" {
            return Err(format!("SupraWall Policy Violation: Tool '{}' explicitly denied.", tool_name).into());
        } else if resp_data.decision == "REQUIRE_APPROVAL" {
            return Err(format!("SupraWall Policy Violation: Tool '{}' requires human approval.", tool_name).into());
        }

        Ok(resp_data)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_client_init_fails_without_env() {
        env::remove_var("SUPRAWALL_API_KEY");
        let client = SupraWallClient::new();
        assert!(client.is_err());
    }

    #[tokio::test]
    async fn test_test_mode_bypass() {
        env::set_var("SUPRAWALL_API_KEY", "sw_test_123");
        let client = SupraWallClient::new().unwrap();
        let res = client.evaluate("test", "tool", serde_json::json!({})).await.unwrap();
        assert_eq!(res.decision, "ALLOW");
    }
}
