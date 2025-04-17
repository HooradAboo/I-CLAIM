Sub ExportZoteroAnnotationToExcel()
    Dim xlApp    As Object
    Dim xlWB     As Object
    Dim xlWS     As Object
    Dim para     As Paragraph
    Dim txt      As String
    Dim rowIndex As Long

    ' Create Excel instance
    Set xlApp = CreateObject("Excel.Application")
    xlApp.Visible = True

    ' Add a new workbook and get its first sheet
    Set xlWB = xlApp.Workbooks.Add
    Set xlWS = xlWB.Sheets(1)

    ' (Optional) add headers:
    xlWS.Cells(1, 1).Value = "Ref."
    xlWS.Cells(1, 2).Value = "Code"
    xlWS.Cells(1, 3).Value = "Quote"

    ' Loop through each paragraph in the active Word document
    rowIndex = 2  ' start at row 2 if you added headers; otherwise use 1
    For Each para In ActiveDocument.Paragraphs
    
        txt = para.Range.text
        
        ' Remove trailing paragraph mark
        If Right(txt, 1) = vbCr Or Right(txt, 1) = Chr(13) Then
            txt = Left(txt, Len(txt) - 1)
        End If
        
        Select Case para.Style
            Case ActiveDocument.Styles("Heading 1")
                ' Case #1: Heading 2 (Skip)
                
            Case ActiveDocument.Styles("Heading 2")
                ' Case #1: Heading 2 (Code)
                rowIndex = rowIndex + 1
                xlWS.Cells(rowIndex, 2).Value = txt
                
            Case ActiveDocument.Styles("Heading 3")
                ' Case #2: Heading 3 (Reference)
                xlWS.Cells(rowIndex, 1).Value = txt
                
            Case Else
                ' Case #3: Normal (Text)
                xlWS.Cells(rowIndex, 3).Value = txt
        End Select
        
    Next para

    ' Clean up
    Set xlWS = Nothing
    Set xlWB = Nothing
    Set xlApp = Nothing
End Sub
