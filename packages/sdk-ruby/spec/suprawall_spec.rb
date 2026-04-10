require 'spec_helper'
require 'suprawall'

RSpec.describe SupraWall do
  it "raises error if API key is missing" do
    SupraWall.api_key = nil
    expect {
      SupraWall.evaluate!(agent_id: "test", tool_name: "test")
    }.to raise_error(SupraWall::Error, /API_KEY is required/)
  end

  it "bypasses for test mode keys" do
    SupraWall.api_key = "sw_test_abc"
    result = SupraWall.evaluate!(agent_id: "test", tool_name: "test")
    expect(result["decision"]).to eq("ALLOW")
  end
end
