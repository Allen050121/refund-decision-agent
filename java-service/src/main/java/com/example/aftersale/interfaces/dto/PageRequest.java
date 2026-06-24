package com.example.aftersale.interfaces.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import lombok.Data;

/**
 * 分页请求基类
 * 所有分页查询请求都可以继承此类
 */
@Data
@Schema(description = "分页请求参数")
public class PageRequest {

    @Schema(description = "页码（从1开始）", example = "1")
    @Min(value = 1, message = "页码必须大于0")
    private Integer pageNum = 1;

    @Schema(description = "每页条数", example = "10")
    @Min(value = 1, message = "每页条数必须大于0")
    @Max(value = 500, message = "每页条数不能超过500")
    private Integer pageSize = 10;

    /**
     * 计算偏移量（用于数据库查询）
     */
    public int getOffset() {
        return (pageNum - 1) * pageSize;
    }
}