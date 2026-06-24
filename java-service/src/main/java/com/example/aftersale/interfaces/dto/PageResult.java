package com.example.aftersale.interfaces.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

import java.util.Collections;
import java.util.List;

/**
 * 分页查询返回对象
 */
@Data
@Schema(description = "分页查询返回对象")
public class PageResult<T> {

    @Schema(description = "数据列表")
    private List<T> records;

    @Schema(description = "总数量")
    private Long total;

    @Schema(description = "当前页码")
    private Integer pageNum;

    @Schema(description = "每页数量")
    private Integer pageSize;

    @Schema(description = "总页数")
    private Integer pages;

    public static <T> PageResult<T> of(List<T> records, long total, int pageNum, int pageSize) {
        PageResult<T> result = new PageResult<>();
        result.setRecords(records);
        result.setTotal(total);
        result.setPageNum(pageNum);
        result.setPageSize(pageSize);
        result.setPages(pageSize > 0 ? (int) ((total + pageSize - 1) / pageSize) : 0);
        return result;
    }

    public static <T> PageResult<T> empty(int pageNum, int pageSize) {
        return of(Collections.emptyList(), 0L, pageNum, pageSize);
    }
}