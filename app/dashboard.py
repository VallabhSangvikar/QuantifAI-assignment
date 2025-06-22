import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import os

# Configure page
st.set_page_config(
    page_title="TechCorp Data Analytics Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
.main-header {
    font-size: 3rem;
    font-weight: bold;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}
.sub-header {
    font-size: 1.5rem;
    color: #ff7f0e;
    margin-bottom: 1rem;
}
.metric-card {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 10px;
    border-left: 5px solid #1f77b4;
}
.quality-good {
    color: #28a745;
    font-weight: bold;
}
.quality-warning {
    color: #ffc107;
    font-weight: bold;
}
.quality-danger {
    color: #dc3545;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load data from SQLite database"""
    try:
        file_path = os.path.join('..', 'ecommerce.db')
        conn = sqlite3.connect(file_path)
        
        # Load all tables
        customers = pd.read_sql_query("SELECT * FROM customers", conn)
        products = pd.read_sql_query("SELECT * FROM products", conn) 
        orders = pd.read_sql_query("SELECT * FROM orders", conn)
        order_items = pd.read_sql_query("SELECT * FROM order_items", conn)
        suppliers = pd.read_sql_query("SELECT * FROM suppliers", conn)
        
        conn.close()
        return customers, products, orders, order_items, suppliers
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None, None, None, None

def create_business_metrics(customers, orders, order_items, products):
    """Calculate key business metrics"""
    
    # Total metrics
    total_customers = len(customers)
    total_orders = len(orders)
    total_revenue = orders['order_total'].sum()
    avg_order_value = orders['order_total'].mean()
    
    # Customer metrics
    active_customers = len(customers[customers['status'] == 'active'])
    customer_retention_rate = (active_customers / total_customers) * 100
    
    # Product metrics
    total_products = len(products)
    active_products = len(products[products['is_active'] == True])
    
    return {
        'total_customers': total_customers,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'avg_order_value': avg_order_value,
        'active_customers': active_customers,
        'customer_retention_rate': customer_retention_rate,
        'total_products': total_products,
        'active_products': active_products
    }

def create_data_quality_metrics(customers, products, orders):
    """Calculate data quality metrics"""
    
    # Customer data quality
    customer_completeness = {
        'email': customers['email'].notna().sum() / len(customers) * 100,
        'phone': customers['phone'].notna().sum() / len(customers) * 100,
        'address': customers['address'].notna().sum() / len(customers) * 100,
    }
    
    # Product data quality
    product_completeness = {
        'description': products['description'].notna().sum() / len(products) * 100,
        'category': products['final_category'].notna().sum() / len(products) * 100,
        'brand': products['brand'].notna().sum() / len(products) * 100,
    }
    
    # Data issues detected
    category_mismatches = products['category_mismatch'].sum() if 'category_mismatch' in products.columns else 0
    active_flag_issues = products['is_active_flag_issue'].sum() if 'is_active_flag_issue' in products.columns else 0
    
    return {
        'customer_completeness': customer_completeness,
        'product_completeness': product_completeness,
        'category_mismatches': category_mismatches,
        'active_flag_issues': active_flag_issues
    }

def create_customer_segmentation_chart(customers):
    """Create customer segmentation visualization"""
    segment_counts = customers['segment'].value_counts()
    
    fig = px.pie(
        values=segment_counts.values,
        names=segment_counts.index,
        title="Customer Segmentation Distribution",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)
    
    return fig

def create_revenue_trend_chart(orders):
    """Create revenue trend over time"""
    # Convert order_date to datetime
    orders['order_date_parsed'] = pd.to_datetime(orders['order_date'], errors='coerce')
    
    # Group by month and sum revenue
    monthly_revenue = orders.groupby(orders['order_date_parsed'].dt.to_period('M'))['order_total'].sum()
    
    fig = px.line(
        x=monthly_revenue.index.astype(str),
        y=monthly_revenue.values,
        title="Monthly Revenue Trend",
        labels={'x': 'Month', 'y': 'Revenue ($)'}
    )
    
    fig.update_traces(line=dict(color='#1f77b4', width=3))
    fig.update_layout(height=400)
    
    return fig

def create_product_performance_chart(products, order_items):
    """Create product performance visualization"""
    # Calculate product sales
    product_sales = order_items.groupby('product_id').agg({
        'quantity': 'sum',
        'total_amount': 'sum'
    }).reset_index()
    
    # Merge with product info
    product_perf = product_sales.merge(
        products[['product_id', 'product_name', 'category', 'final_category']], 
        on='product_id', 
        how='left'
    )
    
    # Top 10 products by revenue
    top_products = product_perf.nlargest(10, 'total_amount')
    
    fig = px.bar(
        top_products,
        x='total_amount',
        y='product_name',
        orientation='h',
        title="Top 10 Products by Revenue",
        labels={'total_amount': 'Revenue ($)', 'product_name': 'Product'}
    )
    
    fig.update_layout(height=500)
    
    return fig

@st.cache_data
def generate_business_insights(customers, products, orders, order_items):
    """Generate AI-powered business insights using LangChain + Gemini"""
    
    try:
        # Initialize LLM
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
        
        # Calculate business metrics for AI analysis
        business_summary = {
            "total_customers": len(customers),
            "total_orders": len(orders),
            "total_revenue": float(orders['order_total'].sum()),
            "avg_order_value": float(orders['order_total'].mean()),
            "customer_segments": customers['segment'].value_counts().to_dict(),
            "customer_status": customers['status'].value_counts().to_dict(),
            "top_categories": order_items.merge(products[['product_id', 'final_category']], on='product_id')['final_category'].value_counts().head(5).to_dict(),
            "monthly_revenue_trend": {str(k): float(v) for k, v in orders.groupby(pd.to_datetime(orders['order_date'], errors='coerce').dt.to_period('M'))['order_total'].sum().tail(6).items()},
            "customer_lifetime_value": customers.groupby('segment')['total_spent'].mean().to_dict(),
            "product_performance": order_items.groupby('product_id')['total_amount'].sum().nlargest(5).to_dict(),
            "geographic_distribution": customers['state'].value_counts().head(5).to_dict() if 'state' in customers.columns else {},
            "inventory_alerts": {
                "low_stock_products": len(products[products['stock_quantity'] < products['reorder_level']]),
                "inactive_products": len(products[products['is_active'] == False]),
                "total_products": len(products)
            }
        }
        
        # Create prompt for business insights
        business_insights_template = """
        You are a senior business analyst for TechCorp, an e-commerce company. 
        Based on the following business metrics and data analysis, provide actionable business insights and recommendations.
        
        Focus on:
        - Revenue optimization opportunities
        - Customer retention strategies  
        - Product performance insights
        - Operational improvements
        - Risk areas and recommendations
        
        Business Metrics Summary:
        {business_data}
        
        Please provide 5-7 specific, actionable insights in a clear, executive-friendly format.
        Each insight should include:
        1. The finding/observation
        2. Business impact
        3. Recommended action
        
        Format as bullet points with clear headings.
        """
        
        prompt = PromptTemplate.from_template(business_insights_template)
        chain = prompt | llm
        
        # Generate insights
        result = chain.invoke({
            "business_data": json.dumps(business_summary, indent=2, default=str)
        })
        return result.content
        
    except Exception as e:
        return f"Error generating AI insights: {str(e)}"

@st.cache_data  
def answer_business_question(question, customers, products, orders, order_items):
    """Answer specific business questions using AI"""
    
    try:
        # Initialize LLM
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
        
        # Prepare relevant data context based on question
        data_context = {
            "customers_summary": {
                "total": len(customers),
                "by_segment": customers['segment'].value_counts().to_dict(),
                "by_status": customers['status'].value_counts().to_dict(),
                "avg_spent": float(customers['total_spent'].mean()),
                "avg_orders": float(customers['total_orders'].mean())
            },
            "products_summary": {
                "total": len(products),
                "categories": products['final_category'].value_counts().to_dict(),
                "avg_price": float(products['price'].mean()),
                "low_stock_count": len(products[products['stock_quantity'] < products['reorder_level']])
            },
            "orders_summary": {
                "total": len(orders),
                "total_revenue": float(orders['order_total'].sum()),
                "avg_order_value": float(orders['order_total'].mean()),
                "status_distribution": orders['status'].value_counts().to_dict()
            }
        }
        
        # Create prompt for question answering
        qa_template = """
        You are a data analyst for TechCorp e-commerce company. Answer the following business question 
        using the provided data context. Be specific, actionable, and include relevant numbers.
        
        Question: {question}
        
        Data Context:
        {data_context}
        
        Provide a clear, concise answer with:
        1. Direct answer to the question
        2. Supporting data/numbers
        3. Actionable recommendation if applicable
        
        Keep response under 200 words.
        """
        
        prompt = PromptTemplate.from_template(qa_template)
        chain = prompt | llm
        
        result = chain.invoke({
            "question": question,
            "data_context": json.dumps(data_context, indent=2, default=str)
        })
        
        return result.content
        
    except Exception as e:
        return f"Error answering question: {str(e)}"

def create_category_analysis(products, order_items):
    """Analyze product categories"""
    # Use final_category (cleaned) for analysis
    category_sales = order_items.merge(
        products[['product_id', 'final_category']], 
        on='product_id'
    ).groupby('final_category').agg({
        'quantity': 'sum',
        'total_amount': 'sum'
    }).reset_index()
    
    fig = px.scatter(
        category_sales,
        x='quantity',
        y='total_amount',
        size='total_amount',
        hover_name='final_category',
        title="Category Performance: Quantity vs Revenue",
        labels={'quantity': 'Total Quantity Sold', 'total_amount': 'Total Revenue ($)'}
    )
    
    fig.update_layout(height=500)
    
    return fig


def main():
    # Header
    st.markdown('<h1 class="main-header">🚀 TechCorp Data Analytics Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("### AI-Powered Business Intelligence from Unified E-Commerce Data")
    
    # Load data
    with st.spinner("Loading data from cleaned database..."):
        customers, products, orders, order_items, suppliers = load_data()
    
    if customers is None:
        st.error("Unable to load data. Please ensure the database file exists.")
        return
    
    # Sidebar for navigation
    st.sidebar.markdown("## 🚀 TechCorp BI")
    st.sidebar.markdown("---")
    page = st.sidebar.radio("📂 Navigation Menu", [
        "📊 Executive Dashboard", 
        "👥 Customer Analytics", 
        "📦 Product Analytics",
        "🔍 Data Quality Report",
        "🤖 AI Insights",
        "📋 Raw Data Explorer"
        ], label_visibility="collapsed")

    
    if page == "📊 Executive Dashboard":
        st.markdown('<h2 class="sub-header">Executive Dashboard</h2>', unsafe_allow_html=True)
        
        # Calculate metrics
        metrics = create_business_metrics(customers, orders, order_items, products)
        
        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="💰 Total Revenue",
                value=f"${metrics['total_revenue']:,.2f}",
                delta=f"${metrics['avg_order_value']:.2f} avg order"
            )
        
        with col2:
            st.metric(
                label="👥 Total Customers",
                value=f"{metrics['total_customers']:,}",
                delta=f"{metrics['customer_retention_rate']:.1f}% active"
            )
        
        with col3:
            st.metric(
                label="📦 Total Orders",
                value=f"{metrics['total_orders']:,}",
                delta=f"${metrics['avg_order_value']:.2f} average"
            )
        
        with col4:
            st.metric(
                label="🏪 Products",
                value=f"{metrics['total_products']:,}",
                delta=f"{metrics['active_products']} active"
            )
        
        # Charts row
        col1, col2 = st.columns(2)
        
        with col1:
            fig_segments = create_customer_segmentation_chart(customers)
            st.plotly_chart(fig_segments, use_container_width=True)
        
        with col2:
            fig_revenue = create_revenue_trend_chart(orders)
            st.plotly_chart(fig_revenue, use_container_width=True)
    
    elif page == "👥 Customer Analytics":
        st.markdown('<h2 class="sub-header">Customer Analytics</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Customer status distribution
            status_counts = customers['status'].value_counts()
            fig_status = px.bar(
                x=status_counts.index,
                y=status_counts.values,
                title="Customer Status Distribution",
                labels={'x': 'Status', 'y': 'Count'}
            )
            st.plotly_chart(fig_status, use_container_width=True)
        
        with col2:
            # Customer segments by total spent
            fig_segment_spend = px.box(
                customers,
                x='segment',
                y='total_spent',
                title="Spending Distribution by Customer Segment"
            )
            st.plotly_chart(fig_segment_spend, use_container_width=True)
        
        # Customer geographic distribution
        if 'state' in customers.columns:
            state_counts = customers['state'].value_counts().head(10)
            fig_geo = px.bar(
                x=state_counts.values,
                y=state_counts.index,
                orientation='h',
                title="Top 10 States by Customer Count"
            )
            st.plotly_chart(fig_geo, use_container_width=True)
    
    elif page == "📦 Product Analytics":
        st.markdown('<h2 class="sub-header">Product Analytics</h2>', unsafe_allow_html=True)
        
        # Product performance chart
        fig_products = create_product_performance_chart(products, order_items)
        st.plotly_chart(fig_products, use_container_width=True)
        
        # Category analysis
        fig_categories = create_category_analysis(products, order_items)
        st.plotly_chart(fig_categories, use_container_width=True)
        
        # Product inventory analysis
        col1, col2 = st.columns(2)
        
        with col1:
            # Stock levels
            fig_stock = px.histogram(
                products,
                x='stock_quantity',
                title="Product Stock Distribution",
                nbins=20
            )
            st.plotly_chart(fig_stock, use_container_width=True)
        
        with col2:
            # Price distribution
            fig_price = px.histogram(
                products,
                x='price',
                title="Product Price Distribution",
                nbins=20
            )
            st.plotly_chart(fig_price, use_container_width=True)
    
    elif page == "🔍 Data Quality Report":
        st.markdown('<h2 class="sub-header">Data Quality Assessment</h2>', unsafe_allow_html=True)
        
        quality_metrics = create_data_quality_metrics(customers, products, orders)
        
        # Data completeness section
        st.subheader("📋 Data Completeness Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Customer Data Completeness:**")
            for field, completeness in quality_metrics['customer_completeness'].items():
                color = "quality-good" if completeness > 80 else "quality-warning" if completeness > 50 else "quality-danger"
                st.markdown(f'<p class="{color}">{field.title()}: {completeness:.1f}%</p>', unsafe_allow_html=True)
        
        with col2:
            st.write("**Product Data Completeness:**")
            for field, completeness in quality_metrics['product_completeness'].items():
                color = "quality-good" if completeness > 80 else "quality-warning" if completeness > 50 else "quality-danger"
                st.markdown(f'<p class="{color}">{field.title()}: {completeness:.1f}%</p>', unsafe_allow_html=True)
        
        # Data issues detected
        st.subheader("🚨 Data Quality Issues Resolved")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                label="Category Mismatches Fixed",
                value=quality_metrics['category_mismatches'],
                delta="Issues resolved"
            )
        
        with col2:
            st.metric(
                label="Active Flag Issues Fixed", 
                value=quality_metrics['active_flag_issues'],
                delta="Inconsistencies resolved"
            )
    
    elif page == "🤖 AI Insights":
        st.markdown('<h2 class="sub-header">AI-Generated Business Insights</h2>', unsafe_allow_html=True)
        
        # Generate AI insights button
        if st.button("🧠 Generate Fresh AI Insights", type="primary"):
            with st.spinner("🤖 AI is analyzing your business data..."):
                ai_insights = generate_business_insights(customers, products, orders, order_items)
                st.session_state.ai_insights = ai_insights
        
        # Display AI insights
        if 'ai_insights' in st.session_state:
            st.success("🤖 **AI Analysis Complete!**")
            st.markdown("### 📊 Business Intelligence Report")
            st.markdown(st.session_state.ai_insights)
        else:
            st.info("👆 Click the button above to generate AI-powered business insights from your data!")
        
        st.markdown("---")
        
        # Interactive AI Query
        st.subheader("💬 Ask AI About Your Business")
        
        # Predefined quick questions
        st.markdown("**Quick Questions:**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💰 Revenue Opportunities"):
                st.session_state.current_question = "What are the biggest revenue opportunities in our data?"
        
        with col2:
            if st.button("👥 Customer Insights"):
                st.session_state.current_question = "Which customer segments should we focus on?"
        
        with col3:
            if st.button("📦 Product Strategy"):
                st.session_state.current_question = "What products should we promote or discontinue?"
        
        # Custom question input
        user_query = st.text_input(
            "Or ask your own question:", 
            placeholder="e.g., Which customers are at risk of churning?",
            key="user_question"
        )
        
        # Handle question answering
        question_to_ask = None
        if user_query:
            question_to_ask = user_query
        elif 'current_question' in st.session_state:
            question_to_ask = st.session_state.current_question
            
        if question_to_ask:
            with st.spinner(f"🤖 AI is analyzing: {question_to_ask}"):
                ai_answer = answer_business_question(question_to_ask, customers, products, orders, order_items)
                st.markdown("### 🎯 AI Response:")
                st.info(ai_answer)
        
        # Clear session state for questions
        if 'current_question' in st.session_state:
            del st.session_state.current_question
    
    elif page == "📋 Raw Data Explorer":
        st.markdown('<h2 class="sub-header">Raw Data Explorer</h2>', unsafe_allow_html=True)
        
        # Table selector
        table_choice = st.selectbox("Select table to explore:", 
                                   ["Customers", "Products", "Orders", "Order Items", "Suppliers"])
        
        if table_choice == "Customers":
            st.subheader(f"Customers Data ({len(customers)} records)")
            st.dataframe(customers, use_container_width=True)
        elif table_choice == "Products":
            st.subheader(f"Products Data ({len(products)} records)")
            st.dataframe(products, use_container_width=True)
        elif table_choice == "Orders":
            st.subheader(f"Orders Data ({len(orders)} records)")
            st.dataframe(orders, use_container_width=True)
        elif table_choice == "Order Items":
            st.subheader(f"Order Items Data ({len(order_items)} records)")
            st.dataframe(order_items, use_container_width=True)
        elif table_choice == "Suppliers":
            st.subheader(f"Suppliers Data ({len(suppliers)} records)")
            st.dataframe(suppliers, use_container_width=True)

if __name__ == "__main__":
    main()




