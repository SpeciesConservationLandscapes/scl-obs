--SCL - Ad Hoc - Duplicate Location and Year (Grid)

;
WITH AdHocDuplicate As
(
SELECT
	CI_GridCellID
	,YEAR(CI_AdHocObservation.StartObservationDate) AS [Year]
	--,COUNT(*) AS [Instances]

FROM
	CI_AdHocObservation
	INNER JOIN CI_UploadedFile ON (CI_AdHocObservation.CI_UploadedFileID=CI_UploadedFile.CI_UploadedFileID)
WHERE
	CI_AdHocObservation.Archive=0
	AND CI_GridCellID IS NOT NULL
	AND CI_UploadedFile.CI_ScenarioID IS NULL


GROUP BY
	CI_GridCellID
	,YEAR(CI_AdHocObservation.StartObservationDate)

HAVING COUNT(DISTINCT CI_AdHocObservation.CI_AdHocObservationID)>1
)

SELECT
	YEAR(CI_AdHocObservation.StartObservationDate) AS [Year]
	,CI_GridCell.CI_GridCellCode AS [Grid Cell Label]
	,CI_AdHocObservation.*

FROM
	CI_AdHocObservation
	INNER JOIN CI_GridCell ON (CI_AdHocObservation.CI_GridCellID=CI_GridCell.CI_GridCellID)
	INNER JOIN AdHocDuplicate ON
	(
		CI_AdHocObservation.CI_GridCellID=AdHocDuplicate.CI_GridCellID
		AND
		YEAR(CI_AdHocObservation.StartObservationDate)=AdHocDuplicate.[Year]
	)
	INNER JOIN CI_UploadedFile ON (CI_AdHocObservation.CI_UploadedFileID=CI_UploadedFile.CI_UploadedFileID)

WHERE
	CI_UploadedFile.CI_ScenarioID IS NULL
	AND CI_AdHocObservation.Archive=0

ORDER BY 1,3