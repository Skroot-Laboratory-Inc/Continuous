class HarvestProperties:
    def __init__(self):
        """ These are the hyperparameters used to determine when to harvest a run. """

        """ Sliding window for the number of points to estimate derivative from. """
        self.derivativePoints = 12*8
        """ Do not estimate a value if we are below this threshold. """
        self.rSquaredThreshold = 0.9
        """ Perpendicular distance from the y=x line to determine if we are past the derivative peak. """
        self.distanceFromYEqualsX = 5
        """ Hours out to stop attempting to predict. """
        self.hoursFromHarvest = 4
        """ How many hours out to attempt to predict a harvest value. """
        """ i.e. hoursFromHarvest + currentTime < harvest_estimate < hoursToHarvestEstimate + currentTime. """
        self.hoursToHarvestEstimate = 2 * 24
        """ Ignore the daysNotToEstimateHarvest if the derivative increases beyond this threshold. """
        self.fastDerivativeThreshold = 0.2
        """ First X days to not provide a harvest estimate. """
        self.daysNotToEstimateHarvest = 3
        """ The number of standard deviations out to predict as the start of the harvest window. """
        self.standardDeviationsToHarvest = 2

