<?php

namespace SupraWall;

use Exception;

class SupraWall {
    private static ?string $apiKey = null;
    private static ?string $apiUrl = null;

    public static function setApiKey(string $key): void {
        self::$apiKey = $key;
    }

    public static function setApiUrl(string $url): void {
        self::$apiUrl = $url;
    }

    public static function evaluate(string $agentId, string $toolName, array $arguments = []): array {
        $apiKey = self::$apiKey ?? getenv('SUPRAWALL_API_KEY');
        $apiUrl = self::$apiUrl ?? getenv('SUPRAWALL_API_URL') ?: 'https://www.supra-wall.com/api/v1/evaluate';

        if (!$apiKey) {
            throw new Exception("SUPRAWALL_API_KEY is required");
        }

        if (str_starts_with($apiKey, 'ag_test_')) {
            return ['decision' => 'ALLOW', 'reason' => 'Test mode bypass'];
        }

        $options = [
            'http' => [
                'header'  => "Content-Type: application/json\r\nAuthorization: Bearer {$apiKey}\r\n",
                'method'  => 'POST',
                'content' => json_encode([
                    'agentId' => $agentId,
                    'toolName' => $toolName,
                    'arguments' => $arguments
                ]),
                'ignore_errors' => true
            ]
        ];

        $context  = stream_context_create($options);
        $result = file_get_contents($apiUrl, false, $context);

        if ($result === false) {
            throw new Exception("SUPRA-WALL Network Error: Failing closed.");
        }

        $data = json_decode($result, true);

        if (($data['decision'] ?? '') === 'DENY') {
            throw new Exception("SUPRA-WALL Policy Violation: Tool '{$toolName}' explicitly denied.");
        } elseif (($data['decision'] ?? '') === 'REQUIRE_APPROVAL') {
            throw new Exception("SUPRA-WALL Policy Violation: Tool '{$toolName}' requires human approval.");
        }

        return $data;
    }
}
