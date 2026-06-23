package com.example.aftersale.domain.shared;

/**
 * 规则版本值对象
 * 用于封装退款规则的版本信息
 */
public record RuleVersion(String ruleId, int version) {

    public RuleVersion {
        if (ruleId == null || ruleId.isBlank()) {
            throw new IllegalArgumentException("规则ID不能为空");
        }
        if (!ruleId.startsWith("REFUND-")) {
            throw new IllegalArgumentException("规则ID格式错误，应以REFUND-开头");
        }
        if (version < 1) {
            throw new IllegalArgumentException("规则版本必须大于0");
        }
    }

    /**
     * 从规则ID和版本创建
     */
    public static RuleVersion of(String ruleId, int version) {
        return new RuleVersion(ruleId, version);
    }

    /**
     * 从字符串解析（如 "REFUND-2026-003@v3"）
     */
    public static RuleVersion parse(String citation) {
        if (citation == null || !citation.contains("@v")) {
            throw new IllegalArgumentException("规则引用格式错误，应为 REFUND-xxx@vn");
        }
        String[] parts = citation.split("@v");
        return new RuleVersion(parts[0], Integer.parseInt(parts[1]));
    }

    /**
     * 获取规则引用字符串（如 "REFUND-2026-003@v3"）
     */
    public String citation() {
        return ruleId + "@v" + version;
    }
}