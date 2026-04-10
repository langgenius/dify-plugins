using System;
using System.Threading.Tasks;
using Xunit;
using SupraWall.Models;

namespace SupraWall.Tests
{
    public class ClientTests
    {
        [Fact]
        public void Constructor_Throws_If_No_ApiKey()
        {
            Environment.SetEnvironmentVariable("SUPRAWALL_API_KEY", null);
            Assert.Throws<ArgumentException>(() => new Client(null));
        }

        [Fact]
        public async Task Evaluate_Bypasses_For_Test_Key()
        {
            var client = new Client("sw_test_123");
            var res = await client.EvaluateAsync("test", "tool");
            Assert.Equal("ALLOW", res.Decision);
        }
    }
}
