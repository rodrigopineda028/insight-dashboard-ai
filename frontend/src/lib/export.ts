import html2canvas from "html2canvas"
import jsPDF from "jspdf"

/**
 * Export a DOM element as PNG image
 */
export async function exportAsPNG(element: HTMLElement, filename: string = "dashboard.png"): Promise<void> {
  try {
    const canvas = await html2canvas(element, {
      backgroundColor: "#09090b", // Dark background
      scale: 2, // Higher quality
      logging: false,
      windowWidth: element.scrollWidth,
      windowHeight: element.scrollHeight,
    })

    // Convert canvas to blob and download
    canvas.toBlob((blob) => {
      if (blob) {
        const url = URL.createObjectURL(blob)
        const link = document.createElement("a")
        link.href = url
        link.download = filename
        link.click()
        URL.revokeObjectURL(url)
      }
    })
  } catch (error) {
    console.error("Error exporting as PNG:", error)
    throw new Error("Failed to export as PNG")
  }
}

/**
 * Export a DOM element as PDF document
 */
export async function exportAsPDF(element: HTMLElement, filename: string = "dashboard.pdf"): Promise<void> {
  try {
    const canvas = await html2canvas(element, {
      backgroundColor: "#09090b",
      scale: 2,
      logging: false,
      windowWidth: element.scrollWidth,
      windowHeight: element.scrollHeight,
    })

    const imgData = canvas.toDataURL("image/png")
    const pdf = new jsPDF({
      orientation: canvas.width > canvas.height ? "landscape" : "portrait",
      unit: "px",
      format: [canvas.width, canvas.height],
    })

    pdf.addImage(imgData, "PNG", 0, 0, canvas.width, canvas.height)
    pdf.save(filename)
  } catch (error) {
    console.error("Error exporting as PDF:", error)
    throw new Error("Failed to export as PDF")
  }
}
