import React, { useState } from 'react';
import Navbar from './components/Navbar'; // Corrected Default Import (No curly braces)
import { Search, Link2, Sparkles, AlertTriangle, CheckCircle, BarChart2, ShieldCheck, Heart, ArrowRight } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('search'); 
  const [searchQuery, setSearchQuery] = useState('');
  const [urlInput, setUrlInput] = useState('');
  
  const [searchResults, setSearchResults] = useState([]);
  const [analysisResult, setAnalysisResult] = useState(null);
  
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState('');

  // Dynamic API Base URL
  const API_BASE = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
    ? "http://127.0.0.1:8000"
    : "";

  // 1. Handle Product Search Query
  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    
    setIsLoading(true);
    setLoadingStep("Searching products on Flipkart...");
    setSearchResults([]);
    setAnalysisResult(null);

    try {
      const res = await fetch(`${API_BASE}/api/search?q=${encodeURIComponent(searchQuery)}`);
      const data = await res.json();
      if (data.status === 'success') {
        setSearchResults(data.results || []);
      } else {
        alert(data.message || "Search failed.");
      }
    } catch (err) {
      alert("Could not connect to the backend. Please verify that the FastAPI server is running.");
    } finally {
      setIsLoading(false);
      setLoadingStep('');
    }
  };

  // 2. Handle Master AI Analysis (NLP + CV + TimeSeries)
  const triggerAnalysis = async (url) => {
    setIsLoading(true);
    setAnalysisResult(null);
    setLoadingStep("Phase 1: Scraping product specifications and images...");
    
    try {
      // Guarded against undefined searchResults state
      const payload = {
        product_url: url,
        products_list: searchResults?.length > 0 ? searchResults : null
      };

      // Simulating step messages during execution
      setTimeout(() => setLoadingStep("Phase 2: Checking image aesthetics with OpenAI CLIP..."), 4000);
      setTimeout(() => setLoadingStep("Phase 3: Forecasting 180-day price trends using Meta Prophet..."), 8000);
      setTimeout(() => setLoadingStep("Phase 4: Collecting customer reviews from Flipkart..."), 12000);
      setTimeout(() => setLoadingStep("Phase 5: Compiling final report using Llama 3.1 & RoBERTa..."), 16000);

      const res = await fetch(`${API_BASE}/api/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      
      const data = await res.json();
      
      if (res.ok && data.status === 'success') {
        setAnalysisResult(data);
        setSearchResults([]); // Clear search cards to keep dashboard clean
      } else {
        alert(data.detail || "Analysis failed.");
      }
    } catch (err) {
      alert("Analysis crashed. Please check that model services are active.");
    } finally {
      setIsLoading(false);
      setLoadingStep('');
    }
  };

  // Helper: SVG Line Graph coordinate mapping (Zero dependencies)
  const renderSVGChart = (history, forecast) => {
    if (!history || !forecast || history.length === 0 || forecast.length === 0) return null;
    
    const hist_points = history.slice(-20); // Last 20 days of history
    const fore_points = forecast; // 14 days of forecast
    
    const all_prices = [
      ...hist_points.map(p => p.y),
      ...fore_points.map(p => p.yhat)
    ];
    const minPrice = Math.min(...all_prices) * 0.98;
    const maxPrice = Math.max(...all_prices) * 1.02;
    const priceRange = maxPrice - minPrice;

    const width = 600;
    const height = 200;
    const padding = 30;

    const getX = (index, total) => padding + (index / (total - 1)) * (width - 2 * padding);
    const getY = (price) => height - padding - ((price - minPrice) / priceRange) * (height - 2 * padding);

    let histPath = "";
    hist_points.forEach((p, idx) => {
      const x = getX(idx, hist_points.length);
      const y = getY(p.y);
      histPath += `${idx === 0 ? 'M' : 'L'} ${x} ${y} `;
    });

    let forePath = "";
    const lastHistX = getX(hist_points.length - 1, hist_points.length);
    const lastHistY = getY(hist_points[hist_points.length - 1].y);
    forePath += `M ${lastHistX} ${lastHistY} `;

    fore_points.forEach((p, idx) => {
      const x = lastHistX + getX(idx, fore_points.length) - padding;
      const y = getY(p.yhat);
      forePath += `L ${x} ${y} `;
    });

    return (
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto bg-dark-bg/50 rounded-xl p-2 border border-white/5">
        <line x1={padding} y1={padding} x2={width-padding} y2={padding} stroke="rgba(255,255,255,0.05)" />
        <line x1={padding} y1={height/2} x2={width-padding} y2={height/2} stroke="rgba(255,255,255,0.05)" />
        <line x1={padding} y1={height-padding} x2={width-padding} y2={height-padding} stroke="rgba(255,255,255,0.08)" />

        {histPath && <path d={histPath} fill="none" stroke="#8b5cf6" strokeWidth="3" className="transition-all duration-500" />}
        {forePath && <path d={forePath} fill="none" stroke="#ec4899" strokeWidth="3" strokeDasharray="5,5" className="transition-all duration-500" />}
      </svg>
    );
  };

  return (
    <div className="min-h-screen bg-dark-bg text-gray-100 flex flex-col">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-extrabold bg-gradient-to-r from-white via-violet-300 to-violet-500 bg-clip-text text-transparent">
            Hi, Jatin
          </h1>
          <p className="text-gray-400 mt-3 text-lg max-w-2xl mx-auto">
            Search for products on Flipkart or paste a direct URL to analyze customer sentiment, image quality, and price forecasting.
          </p>
        </div>

        {/* DUAL INPUT TABS PANEL */}
        <div className="max-w-3xl mx-auto bg-dark-card/60 backdrop-blur-md rounded-2xl p-6 border border-white/5 shadow-2xl mb-12">
          <div className="flex gap-4 mb-6 border-b border-white/5 pb-4">
            <button 
              onClick={() => { setActiveTab('search'); setSearchResults([]); setAnalysisResult(null); }}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-300 ${activeTab === 'search' ? 'bg-accent-violet/20 text-accent-violet border border-accent-violet/30' : 'text-gray-400 hover:text-white'}`}
            >
              <Search className="w-4 h-4" /> Search Products
            </button>
            <button 
              onClick={() => { setActiveTab('url'); setAnalysisResult(null); setSearchResults([]); }}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-300 ${activeTab === 'url' ? 'bg-accent-violet/20 text-accent-violet border border-accent-violet/30' : 'text-gray-400 hover:text-white'}`}
            >
              <Link2 className="w-4 h-4" /> Paste Product URL
            </button>
          </div>

          {/* TAB A: SEARCH INTERFACE */}
          {activeTab === 'search' && (
            <form onSubmit={handleSearch} className="flex gap-2">
              <input 
                type="text" 
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="e.g. Panasonic AC, softtoy, chocolate, headphones"
                className="flex-1 bg-dark-bg/80 border border-white/5 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-accent-violet/50 transition-colors"
              />
              <button type="submit" className="bg-accent-violet hover:bg-accent-violet/90 text-white font-bold text-sm px-6 py-3 rounded-xl flex items-center gap-2 transition-all duration-300 hover:shadow-[0_0_20px_rgba(139,92,246,0.5)]">
                Search <Search className="w-4 h-4" />
              </button>
            </form>
          )}

          {/* TAB B: URL PASTER INTERFACE */}
          {activeTab === 'url' && (
            <div className="flex gap-2">
              <input 
                type="text" 
                value={urlInput}
                onChange={(e) => setUrlInput(e.target.value)}
                placeholder="Paste Flipkart product detail page URL here..."
                className="flex-1 bg-dark-bg/80 border border-white/5 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-accent-violet/50 transition-colors"
              />
              <button 
                onClick={() => triggerAnalysis(urlInput)}
                className="bg-accent-violet hover:bg-accent-violet/90 text-white font-bold text-sm px-6 py-3 rounded-xl flex items-center gap-2 transition-all duration-300 hover:shadow-[0_0_20px_rgba(139,92,246,0.5)]"
              >
                Analyze <Sparkles className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>

        {/* DYNAMIC STEP-BY-STEP PROGRESS LOADER */}
        {isLoading && (
          <div className="max-w-2xl mx-auto bg-dark-card/40 border border-white/5 rounded-2xl p-6 text-center shadow-xl mb-12">
            <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-accent-violet mx-auto mb-4"></div>
            <p className="text-sm font-medium text-gray-300 animate-pulse">{loadingStep}</p>
            <span className="text-xs text-gray-500 mt-2 block">Background AI models running sequentially (~15s)...</span>
          </div>
        )}

        {/* SEARCH RESULTS DYNAMIC GRID CARDS */}
        {searchResults?.length > 0 && !isLoading && (
          <div className="mb-12">
            <h2 className="text-xl font-bold mb-6 text-gray-300">🔍 Select a product to analyze:</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
              {searchResults.map((prod, idx) => (
                <div key={idx} className="bg-dark-card/60 backdrop-blur-sm border border-white/5 rounded-2xl p-4 flex flex-col justify-between hover:scale-[1.02] hover:border-accent-violet/30 transition-all duration-300">
                  <div>
                    {prod.image && (
                      <div className="aspect-square bg-dark-bg/40 rounded-xl overflow-hidden mb-3 flex items-center justify-center p-2">
                        <img src={prod.image} alt={prod.name} className="max-h-full max-w-full object-contain" />
                      </div>
                    )}
                    <h3 className="text-sm font-semibold text-gray-200 line-clamp-2 mb-1">{prod.name}</h3>
                    <p className="text-accent-cyan font-extrabold text-lg mb-4">{prod.price}</p>
                  </div>
                  <button 
                    onClick={() => triggerAnalysis(prod.url)}
                    className="w-full bg-accent-violet/10 hover:bg-accent-violet text-accent-violet hover:text-white font-bold text-xs py-2.5 rounded-xl border border-accent-violet/20 transition-all duration-300"
                  >
                    Analyze Insights <ArrowRight className="w-3 h-3 inline ml-1" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* CORE UNIFIED ANALYSIS DASHBOARD */}
        {analysisResult && !isLoading && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 animate-fade-in">
            
            {/* LEFT COLUMN (lg:5) - Product Info, CV & Price Trends */}
            <div className="lg:col-span-5 flex flex-col gap-8">
              {/* Product Card */}
              <div className="bg-dark-card/50 border border-white/5 rounded-2xl p-6 shadow-xl">
                <span className="text-xs font-bold text-accent-pink uppercase tracking-widest bg-accent-pink/10 px-2.5 py-1 rounded-full mb-3 inline-block">Product Scraped</span>
                <h2 className="text-xl font-bold mb-2 text-gray-100">{analysisResult?.product_details?.name}</h2>
                <h3 className="text-2xl font-black text-accent-cyan mb-4">{analysisResult?.product_details?.price}</h3>
                {analysisResult?.product_details?.image && (
                  <div className="bg-dark-bg/30 border border-white/5 rounded-xl p-4 flex items-center justify-center mb-4">
                    <img src={analysisResult?.product_details?.image} alt="Product" className="max-h-64 object-contain" />
                  </div>
                )}
                {analysisResult?.description && analysisResult?.description !== "N/A" && (
                  <div className="bg-[#121421] rounded-xl p-3 border border-white/5 text-xs text-gray-400">
                    <span className="font-bold text-gray-300 block mb-1">📝 Specs Highlights:</span>
                    "{analysisResult?.description}"
                  </div>
                )}
              </div>

              {/* CV Analysis Card */}
              {analysisResult?.cv_analysis && !analysisResult?.cv_analysis?.error && (
                <div className="bg-dark-card/50 border border-white/5 rounded-2xl p-6 shadow-xl">
                  <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-accent-violet" /> Computer Vision Integrity Check
                  </h3>
                  
                  {/* Integrity Status */}
                  <div className={`p-4 rounded-xl mb-4 border ${analysisResult?.cv_analysis?.consistency_status === "Matched" ? 'bg-green-500/10 border-green-500/20 text-green-400' : 'bg-red-500/10 border-red-500/20 text-red-400'}`}>
                    <div className="flex items-center gap-2 font-bold mb-1">
                      {analysisResult?.cv_analysis?.consistency_status === "Matched" ? <CheckCircle className="w-5 h-5" /> : <AlertTriangle className="w-5 h-5" />}
                      Listing Status: {analysisResult?.cv_analysis?.consistency_status}
                    </div>
                    <p className="text-xs text-gray-400 leading-relaxed">
                      {analysisResult?.cv_analysis?.consistency_status === "Matched" 
                        ? `AI Verified: Product images successfully matched the description with a high consistency score of ${analysisResult?.cv_analysis?.consistency_score}%.`
                        : `Alert: Description mismatched detected. Image alignment is extremely poor (${analysisResult?.cv_analysis?.consistency_score}%).`}
                    </p>
                  </div>

                  {/* Progress bar */}
                  <div className="flex justify-between text-xs font-semibold text-gray-400 mb-1">
                    <span>Aesthetic Score (CLIP)</span>
                    <span>{analysisResult?.cv_analysis?.clip_aesthetic_score}/100</span>
                  </div>
                  <div className="w-full bg-dark-bg/80 h-2 rounded-full overflow-hidden mb-4">
                    <div className="bg-accent-violet h-full" style={{ width: `${analysisResult?.cv_analysis?.clip_aesthetic_score}%` }}></div>
                  </div>

                  <p className="text-xs text-gray-500">
                    Resolution: **{analysisResult?.cv_analysis?.width}x{analysisResult?.cv_analysis?.height}** | Sharpness Metric: **{analysisResult?.cv_analysis?.blur_metric}**
                  </p>
                </div>
              )}

              {/* Time Series Forecasting Card */}
              {analysisResult?.timeseries_analysis && (
                <div className="bg-dark-card/50 border border-white/5 rounded-2xl p-6 shadow-xl">
                  <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                    <BarChart2 className="w-5 h-5 text-accent-pink" /> 14-Day Price Forecast (Prophet)
                  </h3>

                  {/* Buying Signal Banners */}
                  <div className="bg-accent-violet/10 border border-accent-violet/20 rounded-xl p-3 text-sm text-gray-300 font-semibold mb-4 text-center">
                    Signal: {analysisResult?.timeseries_analysis?.indicators?.signal}
                  </div>

                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div className="bg-dark-bg/40 border border-white/5 p-3 rounded-xl text-center">
                      <span className="text-xs text-gray-500 block mb-0.5">Support Level</span>
                      <span className="font-bold text-gray-200">₹{Math.round(analysisResult?.timeseries_analysis?.indicators?.support)}</span>
                    </div>
                    <div className="bg-dark-bg/40 border border-white/5 p-3 rounded-xl text-center">
                      <span className="text-xs text-gray-500 block mb-0.5">Resistance Level</span>
                      <span className="font-bold text-gray-200">₹{Math.round(analysisResult?.timeseries_analysis?.indicators?.resistance)}</span>
                    </div>
                  </div>

                  {/* Native SVG Chart Rendered dynamically */}
                  {renderSVGChart(analysisResult?.timeseries_analysis?.history, analysisResult?.timeseries_analysis?.forecast)}
                  <span className="text-[10px] text-gray-500 text-center block mt-2">
                    Solid Line: Last 20 days history | Dashed Line: 14-day Prophet AI predictions.
                  </span>
                </div>
              )}
            </div>

            {/* RIGHT COLUMN (lg:7) - NLP Insights (Sentiment, Summary & Keywords) */}
            <div className="lg:col-span-7 flex flex-col gap-8">
              {/* Sentiment Card */}
              <div className="bg-dark-card/50 border border-white/5 rounded-2xl p-6 shadow-xl">
                <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
                  <BarChart2 className="w-5 h-5 text-accent-violet" /> Sentiment Analysis (RoBERTa)
                </h3>
                
                <div className="grid grid-cols-3 gap-4 mb-6">
                  <div className="text-center p-3 bg-green-500/5 border border-green-500/10 rounded-xl">
                    <span className="text-xs text-gray-500 block mb-1">Positive 😊</span>
                    <span className="text-2xl font-black text-green-400">{analysisResult?.nlp_analysis?.overall_sentiment?.positive}%</span>
                  </div>
                  <div className="text-center p-3 bg-red-500/5 border border-red-500/10 rounded-xl">
                    <span className="text-xs text-gray-500 block mb-1">Negative 😡</span>
                    <span className="text-2xl font-black text-red-400">{analysisResult?.nlp_analysis?.overall_sentiment?.negative}%</span>
                  </div>
                  <div className="text-center p-3 bg-yellow-500/5 border border-yellow-500/10 rounded-xl">
                    <span className="text-xs text-gray-500 block mb-1">Neutral 😐</span>
                    <span className="text-2xl font-black text-yellow-400">{analysisResult?.nlp_analysis?.overall_sentiment?.neutral}%</span>
                  </div>
                </div>

                {/* Aspect Scorecard inside NLP column */}
                {analysisResult?.nlp_analysis?.absa_scorecard && Object.keys(analysisResult?.nlp_analysis?.absa_scorecard).length > 0 && (
                  <div>
                    <h4 className="text-sm font-bold text-gray-300 mb-3">Aspect-Based Satisfaction Ratings:</h4>
                    <div className="space-y-4">
                      {Object.entries(analysisResult?.nlp_analysis?.absa_scorecard).map(([aspect, data], idx) => (
                        <div key={idx}>
                          <div className="flex justify-between text-xs font-semibold text-gray-400 mb-1">
                            <span>{aspect} (Mentions: {data.count})</span>
                            <span className="text-gray-200">{data.rating}/100</span>
                          </div>
                          <div className="w-full bg-dark-bg/80 h-1.5 rounded-full overflow-hidden">
                            <div className="bg-accent-pink h-full" style={{ width: `${data.rating}%` }}></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Fake review analyzer */}
              {analysisResult?.nlp_analysis?.fake_analysis && (
                <div className="bg-dark-card/50 border border-white/5 rounded-2xl p-6 shadow-xl">
                  <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                    <ShieldCheck className="w-5 h-5 text-accent-cyan" /> Syntactic Spam & Fraud Detection
                  </h3>

                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div className="bg-green-500/5 border border-green-500/10 p-3 rounded-xl text-center">
                      <span className="text-xs text-gray-500 block">Genuine Reviews</span>
                      <span className="text-xl font-bold text-green-400">{analysisResult?.nlp_analysis?.fake_analysis?.real_percent}%</span>
                    </div>
                    <div className="bg-red-500/5 border border-red-500/10 p-3 rounded-xl text-center">
                      <span className="text-xs text-gray-500 block">Flagged Suspicious</span>
                      <span className="text-xl font-bold text-red-400">{analysisResult?.nlp_analysis?.fake_analysis?.fake_percent}%</span>
                    </div>
                  </div>

                  {analysisResult?.nlp_analysis?.fake_analysis?.flagged_reviews && analysisResult?.nlp_analysis?.fake_analysis?.flagged_reviews?.length > 0 ? (
                    <div className="space-y-3">
                      <span className="text-xs font-bold text-gray-400">Flagged Reviews Details:</span>
                      {analysisResult?.nlp_analysis?.fake_analysis?.flagged_reviews.map((f_rev, idx) => (
                        <div key={idx} className="bg-red-500/5 border border-red-500/10 rounded-xl p-3 text-xs leading-relaxed text-gray-300">
                          <p className="italic mb-2">"{f_rev.review}"</p>
                          <span className="text-red-400 font-bold block">Reason: {f_rev.reasons.join(', ')}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-sm text-green-400 bg-green-500/5 border border-green-500/10 p-3 rounded-xl text-center font-semibold">
                      No suspicious/fake reviews detected in the scraped batch!
                    </div>
                  )}
                </div>
              )}

              {/* Llama summary */}
              <div className="bg-dark-card/50 border border-white/5 rounded-2xl p-6 shadow-xl">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-accent-violet" /> AI Reviews Summary (Llama 3.1)
                </h3>
                <div className="bg-dark-bg/30 border border-white/5 rounded-xl p-4 text-sm leading-relaxed text-gray-300">
                  {analysisResult?.nlp_analysis?.ai_summary}
                </div>

                {/* Top themes extracted by spacy */}
                {analysisResult?.nlp_analysis?.top_themes && analysisResult?.nlp_analysis?.top_themes?.length > 0 && (
                  <div className="mt-4">
                    <span className="text-xs font-bold text-gray-500 block mb-2">DYNAMIC EXTRACTED KEYWORDS:</span>
                    <div className="flex flex-wrap gap-2">
                      {analysisResult?.nlp_analysis?.top_themes.map(([word, count], idx) => (
                        <span key={idx} className="bg-dark-bg/80 border border-white/5 text-gray-300 text-xs px-2.5 py-1 rounded-lg">
                          {word} ({count}x)
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Raw Reviews list */}
              {analysisResult?.raw_reviews && analysisResult?.raw_reviews?.length > 0 && (
                <div className="bg-dark-card/50 border border-white/5 rounded-2xl p-6 shadow-xl">
                  <h3 className="text-lg font-bold mb-4">Raw Reviews Feed ({analysisResult?.raw_reviews_count})</h3>
                  <div className="max-h-60 overflow-y-auto space-y-3 pr-2">
                    {analysisResult?.raw_reviews.map((rev, idx) => (
                      <div key={idx} className="bg-dark-bg/20 border border-white/5 rounded-xl p-3 text-xs text-gray-300 leading-relaxed">
                        <strong>{idx + 1}.</strong> {rev}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* --- AI RECOMMENDATIONS SECTION --- */}
            {analysisResult?.recommendations && analysisResult?.recommendations?.length > 0 && (
              <div className="lg:col-span-12 mt-8">
                <h2 className="text-2xl font-bold mb-6 text-gray-300 flex items-center gap-2">
                  <Heart className="w-6 h-6 text-accent-pink fill-accent-pink/10" /> AI Suggested Alternatives
                </h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
                  {analysisResult?.recommendations.map((rec_item, idx) => (
                    <div key={idx} className="bg-dark-card/50 border border-white/5 rounded-2xl p-4 flex flex-col justify-between hover:scale-[1.01] hover:border-accent-pink/30 transition-all duration-300">
                      <div>
                        {rec_item.image && (
                          <div className="aspect-[4/3] bg-dark-bg/30 rounded-xl overflow-hidden mb-3 flex items-center justify-center p-2">
                            <img src={rec_item.image} alt={rec_item.name} className="max-h-full max-w-full object-contain" />
                          </div>
                        )}
                        <h3 className="text-sm font-semibold text-gray-200 line-clamp-2 mb-1">{rec_item.name}</h3>
                        <p className="text-accent-cyan font-extrabold text-lg mb-2">{rec_item.price}</p>
                        
                        {/* Saving Tag */}
                        {rec_item.price_diff_pct > 0 ? (
                          <span className="text-[10px] font-bold text-green-400 bg-green-500/10 px-2 py-0.5 rounded-full mb-3 inline-block">
                            💰 Save {rec_item.price_diff_pct}% compared to current!
                          </span>
                        ) : rec_item.price_diff_pct < 0 ? (
                          <span className="text-[10px] font-bold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded-full mb-3 inline-block">
                            📈 Costs {-rec_item.price_diff_pct}% more
                          </span>
                        ) : (
                          <span className="text-[10px] font-bold text-gray-400 bg-gray-500/10 px-2 py-0.5 rounded-full mb-3 inline-block">
                            Same Price
                          </span>
                        )}
                      </div>
                      
                      <button 
                        onClick={() => triggerAnalysis(rec_item.url)}
                        className="w-full bg-accent-pink/10 hover:bg-accent-pink text-accent-pink hover:text-white font-bold text-xs py-2 rounded-xl border border-accent-pink/20 transition-all duration-300 mt-4"
                      >
                        Scan This Instead 🔍
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}