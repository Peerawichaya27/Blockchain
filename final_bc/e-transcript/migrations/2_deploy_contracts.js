const UniversityCredential = artifacts.require("UniversityCredential");

module.exports = function (deployer) {
    deployer.deploy(UniversityCredential);
};
