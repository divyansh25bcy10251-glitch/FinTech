import { useEffect, useState } from "react";

import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
} from "recharts";

import "./App.css";

function App() {

  // =========================
  // DEMO DATA
  // =========================

  const spendingRatio = [
    { name: "Essential", value: 68.5 },
    { name: "Discretionary", value: 31.5 },
  ];

  const spendingData = [
    { category: "Rent", amount: 1200 },
    { category: "Groceries", amount: 550 },
    { category: "Savings", amount: 500 },
    { category: "Shopping", amount: 400 },
    { category: "Transport", amount: 210 },
  ];

  // =========================
  // SCREEN & DATA STATE
  // =========================

  const [screen, setScreen] = useState("home");
  const [riskScore, setRiskScore] = useState(745); // Dynamic risk score state

  // =========================
  // PROCESSING TIMER & API CALL
  // =========================

  useEffect(() => {
    if (screen === "processing") {
      
      // 1. Call your Django backend while the loader is spinning
      const fetchBackendScore = async () => {
        try {
          const response = await fetch("http://127.0.0.1:8000/api/score/", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            // Sending the mock demo data matching your dashboard metrics
            body: JSON.stringify({
              daily_balance: 1820.50,
              spend_ratio: 0.315,
              income_freq: 7 
            }),
          });

          const data = await response.json();
          console.log("✅ Django Response Received:", data);
          
          // 2. Update state with the ML model's score if successful
          if (data.risk_score) {
            setRiskScore(data.risk_score);
          }
        } catch (error) {
          console.error("❌ Connection failed to Django backend:", error);
        }
      };

      fetchBackendScore();

      // 3. Keep your 3-second delay for the smooth demo loading screen
      const timer = setTimeout(() => {
        setScreen("dashboard");
      }, 3000);

      return () => clearTimeout(timer);
    }
  }, [screen]);

  // =====================================================
  // PROCESSING SCREEN
  // =====================================================

  if (screen === "processing") {
    return (
      <div className="processingPage">
        <div className="processingCard">
          <div className="loader"></div>
          <p className="tag">
            CASH-FLOW ANALYSIS
          </p>
          <h1>
            Analyzing your finances
          </h1>
          <p className="processingText">
            We're analyzing your transaction history and calculating
            your financial risk profile.
          </p>

          {/* Progress Bar */}
          <div className="progressBar">
            <div className="progressFill"></div>
          </div>

          <p className="progressText">
            Analyzing cash flow...
          </p>

          {/* Analysis Steps */}
          <div className="analysisSteps">
            <p>✓ Bank account connected</p>
            <p>✓ Transactions received</p>
            <p>● Calculating financial metrics</p>
            <p>○ Generating risk score</p>
          </div>
        </div>
      </div>
    );
  }

  // =====================================================
  // DASHBOARD SCREEN
  // =====================================================

  if (screen === "dashboard") {
    return (
      <div className="dashboardPage">

        {/* DASHBOARD NAVBAR */}
        <nav className="dashboardNav">
          <h2>CashFlow</h2>
          <div className="dashboardNavRight">
            <span className="demoBadge">
              Demo Account
            </span>
            <button
              onClick={() => setScreen("home")}
            >
              Exit Demo
            </button>
          </div>
        </nav>

        {/* DASHBOARD CONTENT */}
        <main className="dashboardContainer">

          {/* DASHBOARD HEADER */}
          <div className="dashboardHeader">
            <div>
              <p className="dashboardLabel">
                FINANCIAL ASSESSMENT
              </p>
              <h1>
                Your Financial Health
              </h1>
              <p>
                Cash-flow based credit risk assessment
              </p>
            </div>
            <div className="approvedBadge">
              ✓ APPROVED
            </div>
          </div>

          {/* SCORE SECTION */}
          <div className="scoreGrid">

            {/* CASH FLOW SCORE */}
            <div className="dashboardCard scoreCard">
              <p className="cardLabel">
                CASH FLOW SCORE
              </p>

              <div className="scoreNumber">
                {/* Dynamically displaying the score from Django */}
                {riskScore}
                <span>
                  /900
                </span>
              </div>

              <div className="scoreBar">
                <div className="scoreBarFill"></div>
              </div>

              <p className="goodText">
                Excellent financial health
              </p>
            </div>

            {/* RISK ASSESSMENT */}
            <div className="dashboardCard riskCard">
              <p className="cardLabel">
                RISK ASSESSMENT
              </p>
              <h2>
                LOW RISK
              </h2>
              <div className="riskRow">
                <span>
                  Default Probability
                </span>
                <strong>
                  4.2%
                </strong>
              </div>
              <div className="riskRow">
                <span>
                  Credit Limit
                </span>
                <strong>
                  $4,500
                </strong>
              </div>
            </div>

          </div>

          {/* CASH FLOW OVERVIEW */}
          <h2 className="sectionTitle">
            Cash Flow Overview
          </h2>

          <div className="metricsGrid">
            <div className="metricCard">
              <p>
                Average Balance
              </p>
              <h2>
                $1,820.50
              </h2>
              <span>
                Daily average
              </span>
            </div>
            <div className="metricCard">
              <p>
                Monthly Income
              </p>
              <h2>
                $3,600
              </h2>
              <span>
                Recurring income
              </span>
            </div>
            <div className="metricCard">
              <p>
                Net Cash Flow
              </p>
              <h2>
                $1,240
              </h2>
              <span>
                Per month
              </span>
            </div>
            <div className="metricCard">
              <p>
                Income Frequency
              </p>
              <h2>
                Weekly
              </h2>
              <span>
                Stable payouts
              </span>
            </div>
          </div>

          {/* SPENDING ANALYTICS */}
          <h2 className="sectionTitle">
            Spending Analytics
          </h2>

          <div className="chartsGrid">

            {/* DONUT CHART */}
            <div className="chartCard">
              <div className="chartHeader">
                <div>
                  <h3>
                    Essential vs Discretionary
                  </h3>
                  <p>
                    Monthly spending distribution
                  </p>
                </div>
              </div>

              <div className="donutSection">
                <div className="chartContainer">
                  <ResponsiveContainer
                    width="100%"
                    height={250}
                  >
                    <PieChart>
                      <Pie
                        data={spendingRatio}
                        dataKey="value"
                        nameKey="name"
                        cx="50%"
                        cy="50%"
                        innerRadius={65}
                        outerRadius={95}
                        paddingAngle={4}
                      >
                        <Cell fill="#3b82f6" />
                        <Cell fill="#8b5cf6" />
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>

                {/* CHART LEGEND */}
                <div className="chartLegend">
                  <div className="legendItem">
                    <span
                      className="legendDot essentialDot"
                    ></span>
                    <div>
                      <p>
                        Essential
                      </p>
                      <strong>
                        68.5%
                      </strong>
                    </div>
                  </div>

                  <div className="legendItem">
                    <span
                      className="legendDot discretionaryDot"
                    ></span>
                    <div>
                      <p>
                        Discretionary
                      </p>
                      <strong>
                        31.5%
                      </strong>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* BAR CHART */}
            <div className="chartCard">
              <div className="chartHeader">
                <div>
                  <h3>
                    Spending Breakdown
                  </h3>
                  <p>
                    Where your money goes
                  </p>
                </div>
              </div>

              <ResponsiveContainer
                width="100%"
                height={300}
              >
                <BarChart
                  data={spendingData}
                >
                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="rgba(255,255,255,0.08)"
                  />
                  <XAxis
                    dataKey="category"
                    stroke="#718096"
                    tick={{ fontSize: 11 }}
                  />
                  <YAxis
                    stroke="#718096"
                    tick={{ fontSize: 11 }}
                  />
                  <Tooltip />
                  <Bar
                    dataKey="amount"
                    fill="#3b82f6"
                    radius={[5, 5, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>

          </div>

          {/* FINANCIAL BEHAVIOUR */}
          <h2 className="sectionTitle">
            Financial Behaviour
          </h2>

          <div className="behaviourGrid">

            {/* INCOME STABILITY */}
            <div className="behaviourCard">
              <div className="behaviourHeader">
                <div className="behaviourIcon">
                  ↗
                </div>
                <div>
                  <h3>
                    Income Stability
                  </h3>
                  <p>
                    Consistency of incoming funds
                  </p>
                </div>
              </div>

              <div className="behaviourRow">
                <span>
                  Income Frequency
                </span>
                <strong>
                  Weekly
                </strong>
              </div>

              <div className="behaviourRow">
                <span>
                  Recurring Monthly Income
                </span>
                <strong>
                  $3,600
                </strong>
              </div>

              <div className="incomeSources">
                <p>
                  PRIMARY INCOME SOURCES
                </p>
                <div className="sourceTags">
                  <span>
                    Uber Payouts
                  </span>
                  <span>
                    DoorDash Direct
                  </span>
                </div>
              </div>
            </div>

            {/* PAYMENT REGULARITY */}
            <div className="behaviourCard">
              <div className="behaviourHeader">
                <div className="behaviourIcon">
                  ✓
                </div>
                <div>
                  <h3>
                    Payment Regularity
                  </h3>
                  <p>
                    Consistency of essential payments
                  </p>
                </div>
              </div>

              {/* RENT */}
              <div className="paymentItem">
                <span className="checkIcon">
                  ✓
                </span>
                <div>
                  <strong>
                    Rent paid on time
                  </strong>
                  <p>
                    No late payments detected
                  </p>
                </div>
              </div>

              {/* UTILITIES */}
              <div className="paymentItem">
                <span className="checkIcon">
                  ✓
                </span>
                <div>
                  <strong>
                    Utilities paid on time
                  </strong>
                  <p>
                    Consistent payment history
                  </p>
                </div>
              </div>

              {/* MISSED BILLS */}
              <div className="missedBills">
                <span>
                  Missed bills — last 90 days
                </span>
                <strong>
                  0
                </strong>
              </div>
            </div>

          </div>

        </main>
      </div>
    );
  }

  // =====================================================
  // HOME SCREEN
  // =====================================================

  return (
    <div className="app">

      {/* NAVBAR */}
      <nav className="navbar">
        <h2>
          CashFlow
        </h2>
        <div className="navLinks">
          <a href="#home">
            Home
          </a>
          <a href="#how">
            How It Works
          </a>
          <a href="#about">
            About
          </a>
        </div>
      </nav>

      {/* HERO */}
      <main
        className="hero"
        id="home"
      >
        <p className="tag">
          SMARTER CREDIT ASSESSMENT
        </p>
        <h1>
          Your cash flow tells a
          <br />
          better financial story.
        </h1>
        <p className="description">
          Go beyond traditional credit scores. We analyze your real
          income, spending and payment behaviour to provide a fairer
          assessment of your financial health.
        </p>

        <div className="buttons">
          <button className="primaryBtn">
            Connect Bank Account
          </button>
          <button
            className="secondaryBtn"
            onClick={() => setScreen("processing")}
          >
            Try Demo
          </button>
        </div>

        <p className="security">
          🔒 Your banking credentials are never stored.
        </p>
      </main>

    </div>
  );
}

export default App;
