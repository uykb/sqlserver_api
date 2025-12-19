from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from database import get_db
from schemas import RefreshCustomerResponse

router = APIRouter(
    prefix="/api/refresh-customer-info",
    tags=["客户信息刷新"]
)

@router.post("/{ps_no}", response_model=RefreshCustomerResponse)
def refresh_customer_info(
    ps_no: str,
    db: Session = Depends(get_db)
):
    """
    根据销售出库单号刷新客户产品信息
    
    该API会执行以下操作：
    1. 根据提供的销售出库单号 (ps_no)
    2. 更新 tf_pss 表中的供应商产品编号和名称
    3. 从 prdt_cus 表中获取对应客户的产品信息
    4. 返回更新的记录数量
    
    参数:
    - ps_no: 销售出库单号 (路径参数)
    """
    # 验证输入参数
    if not ps_no or ps_no.strip() == "":
        raise HTTPException(
            status_code=400,
            detail="销售出库单号不能为空"
        )
    
    ps_no = ps_no.strip()
    
    try:
        # 执行更新SQL - 表名和字段名均为大写
        sql = text("""
            update a 
            set a.PRD_NO_SUP = b.PRD_NO_SUP,
                a.PRD_NAME_SUP = b.PRD_NAME_SUP
            from TF_PSS a
            left join MF_PSS c on a.PS_NO = c.PS_NO
            left join PRDT_CUS b on a.PRD_NO = b.PRD_NO and b.CUS_NO = c.CUS_NO
            where a.PS_NO = :ps_no
        """)
        
        # 执行更新操作
        result = db.execute(sql, {"ps_no": ps_no})
        updated_records = result.rowcount
        
        # 提交事务
        db.commit()
        
        # 如果更新记录数为0，可能是单号不存在
        if updated_records == 0:
            # 检查单号是否存在
            check_sql = text("SELECT COUNT(*) as count FROM MF_PSS WHERE PS_NO = :ps_no")
            check_result = db.execute(check_sql, {"ps_no": ps_no}).fetchone()
            if check_result and check_result.count == 0:
                raise HTTPException(
                    status_code=404,
                    detail=f"未找到销售出库单: {ps_no}"
                )
        
        # 返回成功响应
        return RefreshCustomerResponse(
            message="客户信息刷新成功",
            ps_no=ps_no,
            updated_records=updated_records,
            timestamp=datetime.now()
        )
        
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        # 回滚事务
        db.rollback()
        # 记录错误日志
        print(f"数据库更新失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"数据库更新失败: {str(e)}"
        )
