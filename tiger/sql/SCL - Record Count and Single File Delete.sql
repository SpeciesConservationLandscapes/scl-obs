--CI - Record Count and Single File Delete

DECLARE
	@FileID INT = 341
	,@Delete INT = 0 --0 check, 1 delete


IF @Delete=0
BEGIN

	SELECT 'CI_UploadedFile' AS [Table],COUNT(*) AS [Records] FROM CI_UploadedFile WHERE CI_UploadedFileID=@FileID
	UNION ALL SELECT 'CI_AdHocObservation' AS [Table],COUNT(*) AS [Records] FROM CI_AdHocObservation WHERE CI_UploadedFileID=@FileID
	UNION ALL SELECT 'CI_CameraTrapDeployment' AS [Table],COUNT(*) AS [Records] FROM CI_CameraTrapDeployment WHERE CI_UploadedFileID=@FileID
	UNION ALL SELECT 'CI_CameraTrapObservation' AS [Table],COUNT(*) AS [Records] FROM CI_CameraTrapObservation WHERE CI_UploadedFileID=@FileID
	UNION ALL SELECT 'CI_SignSurvey' AS [Table],COUNT(*) AS [Records] FROM CI_SignSurvey WHERE CI_UploadedFileID=@FileID
	UNION ALL SELECT 'CI_SignSurveyObservation' AS [Table],COUNT(*) AS [Records] FROM CI_SignSurveyObservation WHERE CI_UploadedFileID=@FileID

END

IF @Delete=1
BEGIN

	DELETE FROM CI_AdHocObservation WHERE CI_UploadedFileID=@FileID
	DELETE FROM CI_CameraTrapDeployment WHERE CI_UploadedFileID=@FileID
	DELETE FROM CI_CameraTrapObservation WHERE CI_UploadedFileID=@FileID
	DELETE FROM CI_SignSurvey WHERE CI_UploadedFileID=@FileID
	DELETE FROM CI_SignSurveyObservation WHERE CI_UploadedFileID=@FileID
	DELETE FROM CI_UploadedFile WHERE CI_UploadedFileID=@FileID

END
