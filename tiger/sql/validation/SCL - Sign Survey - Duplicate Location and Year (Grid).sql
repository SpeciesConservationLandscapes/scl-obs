--SCL - Sign Survey - Duplicate Location and Year (Grid)

;
WITH SignSurveyDuplicate As
(
SELECT
	CI_GridCellID
	,YEAR(CI_SignSurveyObservation.StartDate) AS [Year]
	--,COUNT(*) AS [Instances]

FROM
	CI_SignSurveyObservation
	INNER JOIN CI_SignSurvey ON (CI_SignSurvey.CI_SignSurveyID=CI_SignSurveyObservation.CI_SignSurveyID)
	INNER JOIN CI_UploadedFile ON (CI_SignSurveyObservation.CI_UploadedFileID=CI_UploadedFile.CI_UploadedFileID)
WHERE
	CI_SignSurveyObservation.Archive=0
	AND CI_SignSurvey.Archive=0
	AND CI_GridCellID IS NOT NULL
	AND CI_UploadedFile.CI_ScenarioID IS NULL

GROUP BY
	CI_GridCellID
	,YEAR(CI_SignSurveyObservation.StartDate)

HAVING COUNT(DISTINCT CI_SignSurveyObservation.CI_SignSurveyObservationID)>1
)

SELECT
	YEAR(CI_SignSurveyObservation.StartDate) AS [Year]
	,CI_GridCell.CI_GridCellCode AS [Grid Cell Label]
	--,CI_CameraTrapDeployment.Reference
	,CI_SignSurvey.*
	,CI_SignSurveyObservation.*

FROM
	CI_SignSurveyObservation
	INNER JOIN CI_UploadedFile ON (CI_SignSurveyObservation.CI_UploadedFileID=CI_UploadedFile.CI_UploadedFileID)
	INNER JOIN CI_SignSurvey ON (CI_SignSurvey.CI_SignSurveyID=CI_SignSurveyObservation.CI_SignSurveyID)
	INNER JOIN CI_GridCell ON (CI_SignSurveyObservation.CI_GridCellID=CI_GridCell.CI_GridCellID)
	INNER JOIN SignSurveyDuplicate ON
	(
		CI_SignSurveyObservation.CI_GridCellID=SignSurveyDuplicate.CI_GridCellID
		AND
		YEAR(CI_SignSurveyObservation.StartDate)=SignSurveyDuplicate.[Year]
	)
	
WHERE
	CI_UploadedFile.CI_ScenarioID IS NULL
	AND CI_SignSurveyObservation.Archive=0

ORDER BY 1,3