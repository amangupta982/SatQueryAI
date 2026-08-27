import Header from '../components/Header'
import ComparisonViewer from '../components/ComparisonViewer'

export default function ChangeDetection({ onOpenMobileNav }) {
  return (
    <div className="flex flex-col h-full min-h-0">
      <Header title="Change Detection" status="Temporal analysis between two passes" onOpenMobileNav={onOpenMobileNav} />
      <div className="flex-1 overflow-y-auto p-4 lg:p-6 max-w-4xl">
        <ComparisonViewer />
      </div>
    </div>
  )
}
