import { useNavigate } from 'react-router-dom'
import {
  ArrowRight,
  Upload,
  MessageSquare,
  Clock,
  Layers,
  ShieldCheck,
  Globe,
  ChevronRight,
  Scan,
  Leaf,
  TrendingUp,
} from 'lucide-react'

export default function Dashboard() {
  const navigate = useNavigate()

  return (
    <div className="flex-1 overflow-y-auto bg-[#fafaf8] text-[#162721] selection:bg-[#dce7e1] selection:text-[#162721]">
      {/* ============================================================ */}
      {/* 1. HERO SECTION: FULL-WIDTH SEAMLESS BRAHMAPUTRA SCENE      */}
      {/* ============================================================ */}
      <section className="w-full relative min-h-[420px] sm:min-h-[450px] lg:min-h-[475px] overflow-hidden flex items-center bg-[#f8f8f6] border-b border-[#e5ebe7]">
        {/* Authentic Brahmaputra River Satellite Background across right half */}
        <div
          className="absolute inset-0 bg-cover bg-right sm:bg-center pointer-events-none"
          style={{
            backgroundImage: `url('/hero_brahmaputra_exact_seamless.jpg')`,
          }}
        />

        {/* Content container aligned with main site grid */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-10 py-10 sm:py-12 lg:py-14 relative z-10 w-full">
          <div className="max-w-xl space-y-5">
            {/* Tagline */}
            <div className="text-[11px] font-bold tracking-[0.14em] text-[#75887e] uppercase font-mono">
              FROM EARTH DATA TO MEANINGFUL INSIGHTS
            </div>

            {/* Main Headline */}
            <h1 className="font-display font-extrabold text-3xl sm:text-4xl lg:text-[46px] leading-[1.12] text-[#162721] tracking-tight">
              Understand<br />Satellite Imagery<br />with AI
            </h1>

            {/* Supporting Description */}
            <p className="text-[14px] sm:text-[15px] text-[#4d5f56] leading-relaxed max-w-lg font-body">
              Ask questions about satellite imagery and let SatQuery automatically select the right analysis. Explore our planet with accurate, evidence-based insights from optical and SAR data.
            </p>

            {/* Action Buttons */}
            <div className="flex items-center gap-3 pt-2">
              <button
                onClick={() => navigate('/new-analysis')}
                className="inline-flex items-center gap-2 px-5 py-2.5 bg-[#234238] hover:bg-[#1a342c] text-white text-xs sm:text-[13.5px] font-semibold rounded-xl shadow-sm transition-all hover:translate-y-[-1px] cursor-pointer"
              >
                <span>Start New Analysis</span>
                <ArrowRight size={15} />
              </button>

              <button
                onClick={() => {
                  const el = document.getElementById('how-it-works')
                  el?.scrollIntoView({ behavior: 'smooth' })
                }}
                className="inline-flex items-center gap-1.5 px-4.5 py-2.5 bg-white hover:bg-[#f2f6f4] border border-[#d2dad5] text-[#234238] text-xs sm:text-[13.5px] font-semibold rounded-xl transition-all cursor-pointer"
              >
                <span>Learn More</span>
              </button>
            </div>

            {/* 3 Earth Science Feature Badges */}
            <div className="grid grid-cols-3 gap-3 pt-5 border-t border-[#e2e9e5]/80">
              {/* Badge 1 */}
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-[#e2eae5] text-[#234238] flex items-center justify-center shrink-0">
                  <Leaf size={15} />
                </div>
                <div>
                  <div className="font-bold text-[#162721] text-[11.5px] leading-tight">Real Earth Data</div>
                  <div className="text-[10.5px] text-[#63766c]">Optical & SAR</div>
                </div>
              </div>

              {/* Badge 2 */}
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-[#e2eae5] text-[#234238] flex items-center justify-center shrink-0">
                  <Layers size={15} />
                </div>
                <div>
                  <div className="font-bold text-[#162721] text-[11.5px] leading-tight">AI-Powered Analysis</div>
                  <div className="text-[10.5px] text-[#63766c]">Multi-task & Multi-modal</div>
                </div>
              </div>

              {/* Badge 3 */}
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-[#e2eae5] text-[#234238] flex items-center justify-center shrink-0">
                  <ShieldCheck size={15} />
                </div>
                <div>
                  <div className="font-bold text-[#162721] text-[11.5px] leading-tight">Built for Research</div>
                  <div className="text-[10.5px] text-[#63766c]">Transparent & Auditable</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ============================================================ */}
      {/* MAIN CONTAINER: Capabilities and How It Works                */}
      {/* ============================================================ */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-10 py-14 space-y-16 lg:space-y-20 relative z-10">

        {/* ============================================================ */}
        {/* 2. WHAT SATQUERY CAN DO (CAPABILITIES WITH IMAGES)           */}
        {/* ============================================================ */}
        <section id="capabilities" className="space-y-6">
          <div className="flex items-end justify-between">
            <div>
              <span className="text-[11px] font-bold text-[#8a7b6b] uppercase tracking-widest font-mono block mb-1">
                CAPABILITIES
              </span>
              <h2 className="font-display font-extrabold text-2xl text-[#162721] tracking-tight">
                What SatQuery Can Do
              </h2>
            </div>
            <button
              onClick={() => navigate('/new-analysis')}
              className="text-xs font-semibold text-[#234238] hover:text-[#162721] flex items-center gap-1 transition-colors cursor-pointer"
            >
              <span>See all capabilities</span>
              <ArrowRight size={13} />
            </button>
          </div>

          {/* 4 Cards in a grid with actual imagery at the top */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Card 1: Visual Question Answering */}
            <div
              onClick={() => navigate('/new-analysis', { state: { presetQuery: 'What is the primary land use in this sector?' } })}
              className="group bg-white rounded-xl border border-[#e2e8e4] overflow-hidden shadow-xs hover:shadow-md transition-all cursor-pointer flex flex-col justify-between"
            >
              <div className="h-28 w-full overflow-hidden bg-slate-100">
                <img
                  src="/cap_vqa.jpg"
                  alt="Visual Question Answering"
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
              </div>
              <div className="p-4 space-y-2.5 flex-1 flex flex-col justify-between">
                <div className="space-y-2">
                  <div className="w-7 h-7 rounded-lg bg-[#234238] text-white flex items-center justify-center">
                    <MessageSquare size={14} />
                  </div>
                  <h3 className="font-display font-bold text-sm text-[#162721] group-hover:text-[#234238] transition-colors">
                    Visual Question Answering
                  </h3>
                  <p className="text-xs text-[#5f7168] leading-relaxed">
                    Ask natural-language questions about satellite imagery and get accurate, context-aware answers.
                  </p>
                </div>
                <div className="pt-2 text-xs font-medium text-[#234238] flex items-center gap-1">
                  <span>Learn more</span>
                  <ArrowRight size={12} />
                </div>
              </div>
            </div>

            {/* Card 2: Object Detection */}
            <div
              onClick={() => navigate('/new-analysis', { state: { presetQuery: 'Detect and count all building structures and roads.' } })}
              className="group bg-white rounded-xl border border-[#e2e8e4] overflow-hidden shadow-xs hover:shadow-md transition-all cursor-pointer flex flex-col justify-between"
            >
              <div className="h-28 w-full overflow-hidden bg-slate-100">
                <img
                  src="/cap_detection.jpg"
                  alt="Object Detection"
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
              </div>
              <div className="p-4 space-y-2.5 flex-1 flex flex-col justify-between">
                <div className="space-y-2">
                  <div className="w-7 h-7 rounded-lg bg-[#2f5546] text-white flex items-center justify-center">
                    <Scan size={14} />
                  </div>
                  <h3 className="font-display font-bold text-sm text-[#162721] group-hover:text-[#2f5546] transition-colors">
                    Object Detection
                  </h3>
                  <p className="text-xs text-[#5f7168] leading-relaxed">
                    Locate and identify objects such as buildings, roads, water bodies and more.
                  </p>
                </div>
                <div className="pt-2 text-xs font-medium text-[#234238] flex items-center gap-1">
                  <span>Learn more</span>
                  <ArrowRight size={12} />
                </div>
              </div>
            </div>

            {/* Card 3: Change Analysis */}
            <div
              onClick={() => navigate('/new-analysis', { state: { presetQuery: 'What changed in the built-up area between these two images?' } })}
              className="group bg-white rounded-xl border border-[#e2e8e4] overflow-hidden shadow-xs hover:shadow-md transition-all cursor-pointer flex flex-col justify-between"
            >
              <div className="h-28 w-full overflow-hidden bg-slate-100">
                <img
                  src="/cap_change.jpg"
                  alt="Change Analysis"
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
              </div>
              <div className="p-4 space-y-2.5 flex-1 flex flex-col justify-between">
                <div className="space-y-2">
                  <div className="w-7 h-7 rounded-lg bg-[#ba6c41] text-white flex items-center justify-center">
                    <Clock size={14} />
                  </div>
                  <h3 className="font-display font-bold text-sm text-[#162721] group-hover:text-[#ba6c41] transition-colors">
                    Change Analysis
                  </h3>
                  <p className="text-xs text-[#5f7168] leading-relaxed">
                    Compare imagery from different times to detect and highlight meaningful changes.
                  </p>
                </div>
                <div className="pt-2 text-xs font-medium text-[#234238] flex items-center gap-1">
                  <span>Learn more</span>
                  <ArrowRight size={12} />
                </div>
              </div>
            </div>

            {/* Card 4: Optical + SAR Analysis */}
            <div
              onClick={() => navigate('/new-analysis', { state: { presetQuery: 'Identify flood extent using optical and SAR data.' } })}
              className="group bg-white rounded-xl border border-[#e2e8e4] overflow-hidden shadow-xs hover:shadow-md transition-all cursor-pointer flex flex-col justify-between"
            >
              <div className="h-28 w-full overflow-hidden bg-slate-100">
                <img
                  src="/cap_optical_sar.jpg"
                  alt="Optical + SAR Analysis"
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
              </div>
              <div className="p-4 space-y-2.5 flex-1 flex flex-col justify-between">
                <div className="space-y-2">
                  <div className="w-7 h-7 rounded-lg bg-[#496557] text-white flex items-center justify-center">
                    <Layers size={14} />
                  </div>
                  <h3 className="font-display font-bold text-sm text-[#162721] group-hover:text-[#496557] transition-colors">
                    Optical + SAR Analysis
                  </h3>
                  <p className="text-xs text-[#5f7168] leading-relaxed">
                    Combine optical and SAR imagery for more robust insights, even in challenging conditions.
                  </p>
                </div>
                <div className="pt-2 text-xs font-medium text-[#234238] flex items-center gap-1">
                  <span>Learn more</span>
                  <ArrowRight size={12} />
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ============================================================ */}
        {/* 3. HOW IT WORKS: FROM IMAGES TO INSIGHTS                     */}
        {/* ============================================================ */}
        <section id="how-it-works" className="space-y-8">
          <div>
            <span className="text-[11px] font-bold text-[#8a7b6b] uppercase tracking-widest font-mono block mb-1">
              HOW IT WORKS
            </span>
            <h2 className="font-display font-extrabold text-2xl text-[#162721] tracking-tight">
              From Images to Insights
            </h2>
          </div>

          {/* 3 Open Horizontal Steps with connecting chevrons */}
          <div className="flex flex-col md:flex-row items-start justify-between gap-6 relative">
            {/* Step 01 */}
            <div className="flex-1 space-y-3">
              <div className="flex items-center gap-3.5">
                <span className="w-7 h-7 rounded-full border border-[#c8d4ce] text-[#234238] font-semibold text-xs flex items-center justify-center bg-white shadow-xs">
                  01
                </span>
                <div className="w-13 h-13 rounded-full bg-[#e2eae5] text-[#234238] flex items-center justify-center">
                  <Upload size={22} strokeWidth={2.2} />
                </div>
              </div>
              <h3 className="font-display font-bold text-base text-[#162721] pt-1">
                Upload Imagery
              </h3>
              <p className="text-xs text-[#5f7168] leading-relaxed max-w-[280px]">
                Add one or more satellite images (optical, SAR, or both).
              </p>
            </div>

            {/* Subtle connecting chevron 1 */}
            <div className="hidden md:flex items-center justify-center pt-4 text-[#aab8b0]">
              <ChevronRight size={24} strokeWidth={1.5} />
            </div>

            {/* Step 02 */}
            <div className="flex-1 space-y-3">
              <div className="flex items-center gap-3.5">
                <span className="w-7 h-7 rounded-full border border-[#c8d4ce] text-[#234238] font-semibold text-xs flex items-center justify-center bg-white shadow-xs">
                  02
                </span>
                <div className="w-13 h-13 rounded-full bg-[#e2eae5] text-[#234238] flex items-center justify-center">
                  <MessageSquare size={22} strokeWidth={2.2} />
                </div>
              </div>
              <h3 className="font-display font-bold text-base text-[#162721] pt-1">
                Ask Your Question
              </h3>
              <p className="text-xs text-[#5f7168] leading-relaxed max-w-[280px]">
                Describe what you want to know using natural language.
              </p>
            </div>

            {/* Subtle connecting chevron 2 */}
            <div className="hidden md:flex items-center justify-center pt-4 text-[#aab8b0]">
              <ChevronRight size={24} strokeWidth={1.5} />
            </div>

            {/* Step 03 */}
            <div className="flex-1 space-y-3">
              <div className="flex items-center gap-3.5">
                <span className="w-7 h-7 rounded-full border border-[#c8d4ce] text-[#234238] font-semibold text-xs flex items-center justify-center bg-white shadow-xs">
                  03
                </span>
                <div className="w-13 h-13 rounded-full bg-[#faede2] text-[#b86938] flex items-center justify-center">
                  <TrendingUp size={22} strokeWidth={2.2} />
                </div>
              </div>
              <h3 className="font-display font-bold text-base text-[#162721] pt-1">
                Get AI-Powered Results
              </h3>
              <p className="text-xs text-[#5f7168] leading-relaxed max-w-[290px]">
                SatQuery selects the right analysis, processes the imagery, and provides evidence-based insights.
              </p>
            </div>
          </div>
        </section>

      </div>

      {/* ============================================================ */}
      {/* 4. WHY SATQUERY SECTION: FULL-WIDTH EDGE-TO-EDGE EXACT MATCH */}
      {/* ============================================================ */}
      <section className="w-full relative overflow-hidden bg-[#07132a] text-white min-h-[380px] lg:min-h-[420px] flex items-center border-y border-slate-800/60">
        {/* Authentic Orbital Satellite view of India & Earth */}
        <div
          className="absolute inset-0 bg-cover bg-center pointer-events-none scale-105"
          style={{
            backgroundImage: `url('/earth_india_orbit.jpg')`,
          }}
        />
        {/* Smooth dark space gradient for perfect text contrast on left */}
        <div className="absolute inset-0 bg-gradient-to-r from-[#050f22]/95 via-[#071530]/80 to-[#07132a]/30 pointer-events-none" />
        <div className="absolute inset-0 bg-slate-950/20 pointer-events-none" />

        {/* Centered content inside max-w-7xl matching the site grid */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-10 py-14 sm:py-16 lg:py-20 relative z-10 w-full">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-14 items-center">
            {/* Left Content */}
            <div className="lg:col-span-6 space-y-4">
              <span className="text-xs font-bold uppercase tracking-[0.2em] text-slate-300/90 font-mono block">
                WHY SATQUERY
              </span>
              <h2 className="font-display font-extrabold text-3xl sm:text-4xl text-white tracking-tight leading-tight">
                One Question. The Right Analysis.
              </h2>
              <p className="text-sm sm:text-[15px] text-slate-200/90 leading-relaxed font-body max-w-lg">
                Instead of requiring you to choose a model or analysis method manually, SatQuery interprets your request and automatically routes it to the most appropriate analysis capability.
              </p>
            </div>

            {/* Right Content: 5 Technology Rows with Clean Colored Badges */}
            <div className="lg:col-span-6 space-y-4">
              {/* Item 1: Remote Sensing Imagery */}
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-xl bg-teal-500/20 border border-teal-400/30 text-teal-300 flex items-center justify-center shrink-0 shadow-sm">
                  <Globe size={18} />
                </div>
                <div>
                  <h4 className="font-semibold text-white text-sm">Remote Sensing Imagery</h4>
                  <p className="text-xs text-slate-300/80 mt-0.5">Support for optical and SAR data</p>
                </div>
              </div>

              {/* Item 2: Natural Language Queries */}
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-xl bg-emerald-500/20 border border-emerald-400/30 text-emerald-300 flex items-center justify-center shrink-0 shadow-sm">
                  <MessageSquare size={18} />
                </div>
                <div>
                  <h4 className="font-semibold text-white text-sm">Natural Language Queries</h4>
                  <p className="text-xs text-slate-300/80 mt-0.5">Simple and intuitive</p>
                </div>
              </div>

              {/* Item 3: Multimodal Analysis */}
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-xl bg-emerald-600/20 border border-emerald-400/30 text-emerald-200 flex items-center justify-center shrink-0 shadow-sm">
                  <Layers size={18} />
                </div>
                <div>
                  <h4 className="font-semibold text-white text-sm">Multimodal Analysis</h4>
                  <p className="text-xs text-slate-300/80 mt-0.5">Combined insights from multiple data sources</p>
                </div>
              </div>

              {/* Item 4: Visual Evidence */}
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-xl bg-rose-500/20 border border-rose-400/30 text-rose-300 flex items-center justify-center shrink-0 shadow-sm">
                  <Scan size={18} />
                </div>
                <div>
                  <h4 className="font-semibold text-white text-sm">Visual Evidence</h4>
                  <p className="text-xs text-slate-300/80 mt-0.5">Bounding boxes, change maps, overlays and more</p>
                </div>
              </div>

              {/* Item 5: Auditable AI Workflows */}
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-xl bg-indigo-500/20 border border-indigo-400/30 text-indigo-300 flex items-center justify-center shrink-0 shadow-sm">
                  <ShieldCheck size={18} />
                </div>
                <div>
                  <h4 className="font-semibold text-white text-sm">Auditable AI Workflows</h4>
                  <p className="text-xs text-slate-300/80 mt-0.5">Transparent and reproducible analysis</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ============================================================ */}
      {/* BOTTOM CONTAINER: CTA and Footer                             */}
      {/* ============================================================ */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-10 py-14 space-y-14 relative z-10">
        
        {/* ============================================================ */}
        {/* 5. READY TO EXPLORE? (FINAL CTA BANNER)                      */}
        {/* ============================================================ */}
        <section className="bg-[#eaf1ec] border border-[#d2ded6] rounded-2xl overflow-hidden flex flex-col md:flex-row items-center justify-between shadow-xs">
          {/* Left: Angled Trapezoid with Satellite Illustration */}
          <div className="flex flex-col sm:flex-row items-center gap-2 sm:gap-6 w-full md:w-auto">
            <div
              className="w-40 sm:w-48 h-28 sm:h-32 bg-[#d7e5dc] flex items-center justify-center shrink-0 relative"
              style={{ clipPath: 'polygon(0 0, 100% 0, 80% 100%, 0 100%)' }}
            >
              {/* Satellite Vector */}
              <svg
                width="64"
                height="64"
                viewBox="0 0 80 80"
                fill="none"
                className="transform -rotate-[32deg] drop-shadow-sm"
              >
                <g>
                  <rect x="6" y="32" width="22" height="16" rx="1.5" fill="#2d5849" stroke="#1a342b" strokeWidth="2" />
                  <line x1="13.3" y1="32" x2="13.3" y2="48" stroke="#1a342b" strokeWidth="1.5" />
                  <line x1="20.6" y1="32" x2="20.6" y2="48" stroke="#1a342b" strokeWidth="1.5" />
                  <line x1="6" y1="40" x2="28" y2="40" stroke="#1a342b" strokeWidth="1" />
                </g>

                <line x1="28" y1="40" x2="33" y2="40" stroke="#1a342b" strokeWidth="2.5" />

                <rect x="33" y="28" width="14" height="24" rx="4" fill="#6d9383" stroke="#1a342b" strokeWidth="2.5" />
                <rect x="35" y="33" width="10" height="14" rx="2" fill="#234238" />

                <line x1="47" y1="40" x2="52" y2="40" stroke="#1a342b" strokeWidth="2.5" />

                <g>
                  <rect x="52" y="32" width="22" height="16" rx="1.5" fill="#2d5849" stroke="#1a342b" strokeWidth="2" />
                  <line x1="59.3" y1="32" x2="59.3" y2="48" stroke="#1a342b" strokeWidth="1.5" />
                  <line x1="66.6" y1="32" x2="66.6" y2="48" stroke="#1a342b" strokeWidth="1.5" />
                  <line x1="52" y1="40" x2="74" y2="40" stroke="#1a342b" strokeWidth="1" />
                </g>

                <g transform="rotate(32 40 40)">
                  <path d="M33 55 C33 65, 47 65, 47 55" fill="none" stroke="#1a342b" strokeWidth="2.5" strokeLinecap="round" />
                  <line x1="40" y1="48" x2="40" y2="58" stroke="#1a342b" strokeWidth="2" />
                  <line x1="36" y1="62" x2="44" y2="62" stroke="#1a342b" strokeWidth="2.5" strokeLinecap="round" />
                </g>
              </svg>
            </div>

            {/* Text details */}
            <div className="py-4 px-4 sm:px-0 text-center sm:text-left">
              <span className="text-[11px] font-bold uppercase tracking-wider text-[#234238] font-mono block">
                READY TO EXPLORE?
              </span>
              <h3 className="font-display font-bold text-lg sm:text-xl text-[#162721] tracking-tight mt-0.5">
                Start Analyzing Your Satellite Imagery
              </h3>
              <p className="text-xs sm:text-sm text-[#5f7168] mt-1">
                Upload your data, ask a question, and see what SatQuery can discover.
              </p>
            </div>
          </div>

          {/* Right Action Button */}
          <div className="p-6 shrink-0">
            <button
              onClick={() => navigate('/new-analysis')}
              className="inline-flex items-center gap-2 px-6 py-2.5 bg-[#234238] hover:bg-[#1a342c] text-white text-xs sm:text-[13.5px] font-semibold rounded-xl shadow-sm transition-all hover:translate-y-[-1px] cursor-pointer"
            >
              <span>Start New Analysis</span>
              <ArrowRight size={15} />
            </button>
          </div>
        </section>

        {/* ============================================================ */}
        {/* 6. MINIMAL SCIENTIFIC FOOTER                                 */}
        {/* ============================================================ */}
        <footer className="pt-6 pb-2 border-t border-[#e2e9e5] flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-[#63766c]">
          <div className="flex items-center gap-2.5">
            <div className="text-[#234238] flex items-center justify-center">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
                <circle cx="8" cy="8" r="3.5" fill="#234238" />
                <circle cx="16" cy="8" r="3.5" fill="#234238" />
                <circle cx="8" cy="16" r="3.5" fill="#234238" />
                <circle cx="16" cy="16" r="3.5" fill="#234238" />
              </svg>
            </div>
            <div>
              <span className="font-bold text-[#162721] text-[13px]">SatQuery AI</span>
              <span className="ml-2 text-[#7e9087] text-xs">Satellite Intelligence for Earth Observation</span>
            </div>
          </div>

          <div className="flex items-center gap-6 text-[12px] font-medium text-[#4d5f56]">
            <span className="hover:text-[#234238] cursor-pointer transition-colors">About</span>
            <span className="hover:text-[#234238] cursor-pointer transition-colors">Documentation</span>
            <span className="hover:text-[#234238] cursor-pointer transition-colors">Research</span>
            <span className="hover:text-[#234238] cursor-pointer transition-colors">Contact</span>
            <span className="text-[#4d5f56] flex items-center gap-1.5 ml-2">
              <Globe size={13} />
              <span className="font-mono text-[#7e9087] text-[11px]">v0.1.0</span>
            </span>
          </div>
        </footer>

      </div>
    </div>
  )
}
