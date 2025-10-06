from flask import Flask, render_template, request, jsonify
from option_delta_hedge import DeltaHedge
import io
import base64
import matplotlib.pyplot as plt
import pandas as pd

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # 获取表单数据
        S0 = float(request.form.get('S0', 100))
        K = float(request.form.get('K', 100))
        T = float(request.form.get('T', 1.0))
        r = float(request.form.get('r', 0.05))
        sigma = float(request.form.get('sigma', 0.2))
        option_type = request.form.get('option_type', 'call')
        position = request.form.get('position', 'long')
        
        # 创建Delta对冲实例
        hedge = DeltaHedge(S0, K, T, r, sigma, option_type, position)
        results = hedge.simulate_delta_hedge(252)
        
        # 生成图表
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        ax1.plot(results['时间'], results['标的价格'])
        ax1.set_title('标的价格路径')
        ax1.set_xlabel('时间')
        ax1.set_ylabel('价格')
        
        ax2.plot(results['时间'], results['Delta'], label='Delta')
        ax2.plot(results['时间'], results['对冲头寸']/100, label='对冲头寸(手)')
        ax2.set_title('Delta和对冲头寸变化')
        ax2.set_xlabel('时间')
        ax2.set_ylabel('数值')
        ax2.legend()
        
        plt.tight_layout()
        
        # 将图表转换为base64字符串
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
        plt.close()
        
        # 准备表格数据
        table_data = results.head().to_html(classes='table table-striped')
        
        return render_template('result.html', 
                             plot_url=plot_url, 
                             table_data=table_data,
                             results=results.to_dict('records'))
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)