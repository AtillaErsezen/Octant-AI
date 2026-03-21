import SectionExcerpt from './SectionExcerpt';

const EXPECTED_SECTIONS = [
  { id: 'Abstract', label: 'Abstract & Summary' },
  { id: '1_Introduction', label: '1. Introduction' },
  { id: '2_Literature_Review', label: '2. Literature Evaluation' },
  { id: '3_Data_and_Universe', label: '3. Data and Universe' },
  { id: '4_Methodology', label: '4. Methodology' },
  { id: '5_Results', label: '5. Results' },
  { id: '6_Discussion', label: '6. Discussion' },
  { id: '7_Conclusions', label: '7. Conclusions' },
  { id: 'Appendix_A', label: 'Appendix A (Math)' },
  { id: 'Appendix_B', label: 'Appendix B (Stats)' },
  { id: 'Appendix_C', label: 'Appendix C (Citations)' },
  { id: 'Appendix_D', label: 'Appendix D (Code)' }
];

export default function ReportOutline({ sections }: { sections: any[] }) {
  return (
    <div className="flex flex-col gap-3">
      {EXPECTED_SECTIONS.map(req => {
        const generated = sections.find(s => s.section === req.id);
        const isActive = !generated && sections.length > 0 && sections.length < EXPECTED_SECTIONS.length;
        
        return (
          <div key={req.id} className="relative">
             <div className="flex items-center gap-2 mb-1">
               <div className={`w-1.5 h-1.5 rounded-full ${generated ? 'bg-octGreen' : isActive ? 'bg-blue-500 animate-pulse' : 'bg-gray-700'}`} />
               <span className={`text-xs font-semibold ${generated ? 'text-gray-300' : 'text-gray-600'}`}>{req.label}</span>
             </div>
             {generated && (
               <SectionExcerpt content={generated.content} />
             )}
          </div>
        );
      })}
    </div>
  );
}
